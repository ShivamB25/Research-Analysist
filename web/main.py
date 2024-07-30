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

def extract_urls(text):
    link_pattern = re.compile(r'https?://[^\s,\'")]+')
    return link_pattern.findall(text)

async def main():
    # Initialize agents
    search_agent = SearchAgent()
    scraper_agent = ScraperAgent()

    # Initialize data manager
    data_manager = DataManager()

    # Get main query
    main_query = "Spheron Network" ## replace with topic you want to discuss

    all_links = set()  # Use a set to automatically handle duplicates

    # Perform initial search
    initial_search_results = search_agent.search(main_query)
    initial_urls = extract_urls(str(initial_search_results))
    
    # Print initial URLs and add to all_links
    custom_print("Initial search URLs:")
    for url in initial_urls:
        custom_print(url)
        all_links.add(url)

    # Generate follow-up questions
    follow_up_questions = search_agent.generate_follow_up_questions(main_query)

    # Perform searches for follow-up questions
    for i, question in enumerate(follow_up_questions):
        custom_print(f"\nFollow-up question {i+1}: {question}")
        results = search_agent.search(question)
        
        # Use regex to extract URLs from the search results
        urls = extract_urls(str(results))[:10]  # Limit to top 10 results
        
        custom_print("URLs:")
        for url in urls:
            custom_print(url)
            all_links.add(url)

    custom_print("\nSearch process completed.")

    # Convert set to list
    unique_links = list(all_links)

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