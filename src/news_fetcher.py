import os
from dotenv import load_dotenv
from newsapi import NewsApiClient
import json

# Load environment variables from .env file
load_dotenv()

def fetch_news(api_key: str, query: str, from_date: str, to_date: str, output_path: str):
    """
    Fetches news articles from NewsAPI for a given query and date range.

    Args:
        api_key (str): Your NewsAPI API key.
        query (str): The search query (e.g., 'crypto', 'Bitcoin').
        from_date (str): The start date for articles (YYYY-MM-DD).
        to_date (str): The end date for articles (YYYY-MM-DD).
        output_path (str): The path to save the fetched news data (JSON file).
    """
    newsapi = NewsApiClient(api_key=api_key)

    all_articles = newsapi.get_everything(
        q=query,
        from_param=from_date,
        to=to_date,
        language='en',
        sort_by='publishedAt',
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)

    print(f"Successfully fetched {len(all_articles['articles'])} articles and saved to {output_path}")

if __name__ == '__main__':
    # This is an example of how to run the fetcher directly
    # You will need to have a .env file with NEWS_API_KEY="your_api_key"
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        raise ValueError("NEWS_API_KEY not found in .env file. Please add it.")

    # Define parameters for the news fetch
    QUERY = 'cryptocurrency'
    FROM_DATE = '2024-06-01'
    TO_DATE = '2024-07-01'
    OUTPUT_DIR = os.path.join('..', '..', 'data', 'raw_news')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"{QUERY}_{FROM_DATE}_{TO_DATE}.json")

    fetch_news(api_key, QUERY, FROM_DATE, TO_DATE, OUTPUT_PATH)
