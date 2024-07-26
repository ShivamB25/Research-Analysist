from crewai import Task
from pydantic import BaseModel

class ResearchTasks:

    def string_cleanup(self, values : str) -> str:
        if len(values) >= 500:
            return values[:500]
        return values

    def create_context_task(self, agent, research_data : str) -> BaseModel:
        research_data = self.string_cleanup(research_data)
        
        context_task = Task(
            description = f"Research data: {research_data}...",
            expected_output = "Create a structured index of main topics and subtopics based on the research data",
            agent = agent
        )

        return context_task

    def create_simple_summary_context(self, agent, research_data : str):
        context_task = Task(
            description = f"Research data:\n```\n{research_data}\n```",
            expected_output = "Create a short and consise summary detailing the topics and its subtopics, based on the research data",
            agent = agent
        )

        return context_task

    def index_generation_task(self, agent, research_data : str, summaryy_resarch : str):
        #print(":>", type(agent), type(research_data))
        summaryy_resarch = self.string_cleanup(summaryy_resarch)
        context_task = self.create_context_task(agent, research_data)
        return Task(
            description=f"Generate a structured index of topics and subtopics based on the context and the following summary:\n```{summaryy_resarch}\n```",
            agent=agent,
            expected_output="A JSON string representing a dictionary of main topics and subtopics",
            context=[
                context_task
            ]
        )

    def topic_summary_task(self, agent, research_data, main_topic, subtopics):
        context_task = self.create_context_task(agent, research_data)
        return Task(
            description=f"Generate a brief and concise summary for the main topic: '{main_topic}' including the following subtopics: {', '.join(subtopics)}",
            agent=agent,
            expected_output="A concise summary of the main topic, approximately 2-3 paragraphs in length",
            context=[context_task]
        )

    def detailed_subtopic_task(self, agent, research_data, main_topic, subtopic):
        context_task = self.create_context_task(agent, research_data)
        return Task(
            description=f"Produce detailed content for subtopic: {subtopic} on the main topic: {main_topic}",
            agent=agent,
            expected_output="Create detailed content for the given subtopic. The content should be informative, well-structured, and about 2-3 paragraphs long",
            context=[
                context_task
            ]
        )