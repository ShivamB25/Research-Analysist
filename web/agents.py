# agents.py

from crewai import Agent, Task
from tools import search_tool, scrape_tool
from langchain_openai import ChatOpenAI
from crewai_tools import BaseTool
class SearchAgent:
    def __init__(self):
        self.agent = Agent(
            role='Web Searcher',
            goal='Find relevant web pages for given queries and generate follow-up questions',
            backstory='Expert at using search engines to find relevant information and generating insightful questions',
            tools=[search_tool],
            verbose=True,
            llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.4)
        )

    def search(self, query):
        task = Task(
            description=f"Search for: {query}",
            expected_output="A list of top 10 search results."
        )
        result = self.agent.execute_task(task)
        return result

    def generate_follow_up_questions(self, main_query):
        task = Task(
            description=f"Generate 10 relevant and insightful follow-up questions for the main query: '{main_query}'",
            expected_output="A list of 10 follow-up questions, one per line."
        )
        result = self.agent.execute_task(task)
        return result.split('\n')

class ContextGeneratorAgent:
    def __init__(self):
        self.agent = Agent(
            role='Context Generator',
            goal='Generate comprehensive context from scraped data',
            backstory='Expert at synthesizing information from multiple sources and generating insightful analysis',
            verbose=True,
            llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)
        )

    def generate_context(self, data):
        task = Task(
            description=f"Analyze the following data and generate a comprehensive context:\n\n{data}",
            expected_output="A detailed context document synthesizing information from all sources."
        )
        return self.agent.execute_task(task)

class ScraperAgent:
    def __init__(self):
        self.agent = Agent(
            role='Web Scraper',
            goal='Extract summarised content from web pages asynchronouslyshort and concise. only useful to the topic, not extra stuff like html, write as less as possible',
            backstory='Skilled at parsing HTML and extracting summarised . short and concise,only useful to the topic, not extra stuff like html, u can be as less as possible',
            tools=[scrape_tool],
            verbose=True,
            llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.4, max_tokens=500),
            
        )

    async def scrape_urls(self, urls):
        return await scrape_tool._run(urls)
class WebScraper(BaseTool):
    name: str = "Web Scraper"
    description: str = "Scrape content from given URLs asynchronously.short and concise as less as possble "

    async def scrape_url(self, session, url):
        try:
            async with session.get(url, timeout=10) as response:
                content = await response.read()
                soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
                text = soup.get_text(separator='\n', strip=True)
                return text[:10000]  # Limit to first 10000 characters
        except Exception as e:
            return f"Failed to scrape {url}: {str(e)}"

    async def _run(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.scrape_url(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
        return results

scrape_tool = WebScraper()