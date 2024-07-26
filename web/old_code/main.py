import asyncio
from dotenv import load_dotenv
load_dotenv()
from agents import SearchAgent, ScraperAgent, ContextGeneratorAgent
from data_manager import DataManager

async def main():
    # Initialize data manager
    data_manager = DataManager()

    # Initialize agents
    search_agent = SearchAgent()
    scraper_agent = ScraperAgent()
    context_generator_agent = ContextGeneratorAgent()

    # Get main query from user
    # main_query = input("Enter your main query: ")
    main_query = "decentralised network"
    data_manager.set_main_query(main_query)

    # Perform initial search
    initial_search_results = search_agent.search(main_query)
    initial_urls = [item['link'] for item in initial_search_results if 'link' in item]

    # Save initial search links
    data_manager.save_links(initial_urls, 'initial_search_links.json')

    # Scrape content from initial search URLs
    initial_scraped_content = await scraper_agent.scrape_urls(initial_urls)
    data_manager.set_main_query_content(initial_scraped_content)

    # Generate follow-up questions
    follow_up_questions = search_agent.generate_follow_up_questions(main_query)
    for question in follow_up_questions:
        data_manager.add_follow_up_question(question)

    # Perform searches for follow-up questions
    follow_up_search_results = []
    for question in follow_up_questions:
        follow_up_search_results.append(search_agent.search(question))

    # Extract URLs from follow-up search results
    follow_up_urls = []
    for result in follow_up_search_results:
        urls = [item['link'] for item in result if 'link' in item]
        follow_up_urls.extend(urls[:10])  # Limit to top 10 results per question

    # Save follow-up search links
    data_manager.save_links(follow_up_urls, 'follow_up_search_links.json')

    # Scrape content from follow-up URLs
    follow_up_scraped_content = await scraper_agent.scrape_urls(follow_up_urls)

    # Store scraped content in data manager
    for i, question in enumerate(follow_up_questions):
        for url, content in follow_up_scraped_content.items():
            data_manager.add_website_content(i, url, content)

    # Save final data
    data_manager.save_data()

    print("Process completed. Results saved in scraped_data.json")

if __name__ == "__main__":
    asyncio.run(main())