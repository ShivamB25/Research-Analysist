from crewai import Agent
from textwrap import dedent
from langchain_openai import ChatOpenAI
from langchain_community.llms import OpenAI
class ResearchAgents:
    def __init__(self):
        self.default_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.4)
        
    def index_agent(self):
        return Agent(
            role='Index Generation Specialist',
            goal='Generate a structured index of topics and subtopics, minimum of 10 topics.',
            backstory='Expert in organizing and structuring complex information',
            verbose=True,
            llm=self.default_llm
        )

    def summary_agent(self):
        return Agent(
            role='Topic Summary Specialist',
            goal='Create brief starting point summaries for main topics',
            backstory='Skilled in distilling complex information into concise summaries',
            verbose=True,
            llm=self.default_llm
        )

    def detail_agent(self):
        return Agent(
            role='Detailed Content Writer',
            goal='Produce in-depth content for subtopics',
            backstory='Expert in creating comprehensive and informative content',
            verbose=True,
            llm=self.default_llm
        )