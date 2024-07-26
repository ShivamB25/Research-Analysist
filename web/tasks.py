from textwrap import dedent
from crewai import Task

class InitialSearchTask:
    def __init__(self, agent, main_query):
        self.task = Task(
            description=f"Perform an internet search for the main query: '{main_query}' and collect the top 5 results.",
            expected_output="A list of top 5 search results for the main query.",
            agent=agent
        )

class FollowUpSearchTask:
    def __init__(self, agent, question):
        self.task = Task(
            description=f"Perform an internet search for the follow-up question: '{question}' and collect the top 5 results.",
            expected_output="A list of top 5 search results for the follow-up question.",
            agent=agent
        )

class ScrapingTasks:
    def create_scraping_task(self, agent, url):
        return Task(
            description=dedent(f"""
                Scrape the content from the following URL and return the text:
                URL: {url}
            """),
            agent=agent
        )

class ContextGenerationTask:
    def __init__(self, agent, data):
        self.task = Task(
            description=f"Analyze the scraped data and generate a comprehensive context. Data: {data}",
            expected_output="A detailed context document synthesizing information from all sources.",
            agent=agent
        )