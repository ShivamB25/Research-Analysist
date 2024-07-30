import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from crewai import Crew
from dotenv import load_dotenv
from pylatex import Document, Section, Subsection, Command, Package, NewPage
from pylatex.utils import NoEscape
import subprocess
import requests
from agents import ResearchAgents
from tasks import ResearchTasks

load_dotenv()

class ResearchReportCrew:
    def __init__(self, data_source):
        self.data_source = data_source
        self.tasks = ResearchTasks()
        self.agents = ResearchAgents()

    def extract_json(self, text):
        json_match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        json_match = re.search(r'({.*})', text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        return None

    def run(self):
        # Read research data
        print("Reading research data...")
        with open(self.data_source, 'r') as file:
            research_data = file.read()

        # Create crew
        crew = Crew(
            agents=[self.agents.index_agent(), self.agents.summary_agent(), self.agents.detail_agent()],
            tasks=[],
            verbose=True
        )

        # Generate summary of the research data 
        ssmx_task = self.tasks.create_simple_summary_context(self.agents.summary_agent(), research_data)
        crew.tasks = [ssmx_task]
        ssmx_result = crew.kickoff()
        ssmx_result = str(ssmx_result)
        ssmx_result = ssmx_result.strip()
        summary_of_research_result = ssmx_result.replace("\n", " ")

        # Generate index structure
        print("Generating index structure...")
        index_task = self.tasks.index_generation_task(self.agents.index_agent(), research_data, summary_of_research_result)
        crew.tasks = [index_task]
        index_result = crew.kickoff()
        
        try:
            jsox_string = str(index_result)
            index_structure = json.loads(jsox_string)
        except json.JSONDecodeError:
            print("## Error parsing JSON. Attempting to extract JSON with regex...")
            jsox_string = self.extract_json(jsox_string)
            if jsox_string:
                try:
                    index_structure = json.loads(jsox_string)
                except json.JSONDecodeError:
                    print("## Error at parsing JSON after regex extraction:")
                    print(jsox_string)
                    print("###")
                    raise ValueError("Could not extract JSON from the index result")
            else:
                print("## Error at extracting JSON with regex:")
                print(jsox_string)
                print("###")
                raise ValueError("Could not extract JSON from the index result")

        # Generate content
        print("Generating content...")
        content = []
        for main_topic, subtopics in index_structure.items():
            topic_content = self.process_topic(crew, research_data, main_topic, subtopics)
            content.append(topic_content)
            print(f"Completed processing for topic: {main_topic}")

        # Generate LaTeX document
        print("Generating LaTeX document...")
        doc = self.create_latex_document(content)

        # Generate PDF
        doc.generate_pdf('research_report', clean_tex=False)

        print("Research report LaTeX document generated: research_report.pdf")
        return "Research report generation complete."

    def process_topic(self, crew, research_data, main_topic, subtopics):
        print(f"Processing main topic: {main_topic}")
        
        # Generate brief summary for main topic
        summary_task = self.tasks.topic_summary_task(self.agents.summary_agent(), research_data, main_topic, subtopics)
        crew.tasks = [summary_task]
        summary_result = crew.kickoff()
        summary = str(summary_result).strip()
        
        topic_content = {
            "main_topic": main_topic,
            "summary": summary,
            "subtopics": []
        }
        
        for subtopic in subtopics:
            print(f"Processing subtopic: {subtopic}")
            detail_task = self.tasks.detailed_subtopic_task(self.agents.detail_agent(), research_data, main_topic, subtopic)
            crew.tasks = [detail_task]
            detail_result = crew.kickoff()
            detailed_content = str(detail_result).strip()
            
            topic_content["subtopics"].append({
                "name": subtopic,
                "content": detailed_content
            })
        
        return topic_content

    def create_latex_document(self, content):
        doc = Document()
        doc.packages.append(Package('geometry', options=['margin=1in']))
        doc.packages.append(Package('hyperref'))
        doc.preamble.append(Command('title', 'Research Report'))
        doc.preamble.append(Command('author', 'AI Research Team'))
        doc.preamble.append(Command('date', NoEscape(r'\today')))
        doc.append(NoEscape(r'\maketitle'))
        doc.append(NewPage())
        
        # Add table of contents
        doc.append(NoEscape(r'\tableofcontents'))
        doc.append(NewPage())

        for topic in content:
            with doc.create(Section(topic['main_topic'])):
                doc.append(topic['summary'])
                for subtopic in topic['subtopics']:
                    with doc.create(Subsection(subtopic['name'])):
                        doc.append(subtopic['content'])
            doc.append(NewPage())

        return doc

if __name__ == "__main__":
    data_source = 'scraped_data.json'
    research_crew = ResearchReportCrew(data_source)
    result = research_crew.run()
    print(result)

    # Upload the file using pyupload
    try:
        output = subprocess.check_output(['pyupload', data_source, '--host=catbox'], universal_newlines=True)
        print(output)

        # Use regex to extract the link from the output
        match = re.search(r'Your link : (https?://\S+)', output)
        if match:
            file_link = match.group(1)
            print(f"Extracted link: {file_link}")

            # Create Overleaf document
            overleaf_url = f"https://www.overleaf.com/docs?snip_uri={file_link}"
            response = requests.get(overleaf_url)
            
            if response.status_code == 200:
                print(f"Overleaf document created successfully. URL: {overleaf_url}")
            else:
                print(f"Failed to create Overleaf document. Status code: {response.status_code}")
        else:
            print("Failed to extract link from pyupload output")
    except subprocess.CalledProcessError as e:
        print(f"Error running pyupload: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")