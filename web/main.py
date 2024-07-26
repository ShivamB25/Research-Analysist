import asyncio
from dotenv import load_dotenv
import re
import json
import io
from contextlib import redirect_stdout
import os

load_dotenv()
from agents import SearchAgent, ScraperAgent
from data_manager import DataManager

output_buffer = io.StringIO()

# Load character limit from .env file
CHAR_LIMIT = int(os.getenv('CHAR_LIMIT', 508000))  # Default to 508000 if not set

def custom_print(*args, **kwargs):
    print(*args, **kwargs, file=output_buffer)
    print(*args, **kwargs)  # Still print to console

async def main():
    # Initialize agents
    search_agent = SearchAgent()
    scraper_agent = ScraperAgent()

    # Initialize data manager
    data_manager = DataManager()

    # Get main query
    main_query = "decentralised gpu network" ## replace with topic you want to disucss

    # Perform initial search
    initial_search_results = search_agent.search(main_query)
    initial_urls = [item['link'] for item in initial_search_results if 'link' in item]
    
    # Print initial URLs
    custom_print("Initial search URLs:")
    for url in initial_urls:
        custom_print(url)

    # Generate follow-up questions
    follow_up_questions = search_agent.generate_follow_up_questions(main_query)

    # Perform searches for follow-up questions
    for i, question in enumerate(follow_up_questions):
        custom_print(f"\nFollow-up question {i+1}: {question}")
        results = search_agent.search(question)
        urls = [item['link'] for item in results if 'link' in item][:10]  # Limit to top 10 results
        custom_print("URLs:")
        for url in urls:
            custom_print(url)

    custom_print("\nSearch process completed.")

    # Get the captured output
    text_output = output_buffer.getvalue()

    # Regular expression to capture links
    link_pattern = re.compile(r'https?://[^\s,\'")]+')

    # Find all links in the text
    links = link_pattern.findall(text_output)

    # Remove duplicates by converting the list to a set and back to a list
    unique_links = list(set(links))

    # Store the links in a JSON file
    with open('links.json', 'w') as json_file:
        json.dump(unique_links, json_file, indent=4)

    print(f"Extracted {len(unique_links)} unique links.")

    # Initialize character counter
    total_chars = 0

    # Scrape content from URLs
    scraped_content = []
    for link in unique_links:
        content_list = await scraper_agent.scrape_urls([link])
        content = content_list[0] if content_list else ""

        content_length = len(content)
        
        if total_chars + content_length > CHAR_LIMIT:
            break
        
        scraped_content.append(content)
        total_chars += content_length

    data_manager.set_scraped_content(scraped_content)

    # Save final data
    data_manager.save_data()

    print("Scraping completed. Results saved in scraped_data.json")

if __name__ == "__main__":
    asyncio.run(main())