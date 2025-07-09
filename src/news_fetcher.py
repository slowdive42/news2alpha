import os
import json
import yaml
import requests
from dotenv import load_dotenv
from newsapi import NewsApiClient

# Load environment variables from .env file
load_dotenv()

def _fetch_newsapi_news(api_key: str, query: str, from_date: str, to_date: str) -> list:
    """Fetches news articles from NewsAPI."""
    print("Fetching news from NewsAPI...")
    newsapi = NewsApiClient(api_key=api_key)
    response = newsapi.get_everything(
        q=query,
        from_param=from_date,
        to=to_date,
        language='en',
        sort_by='publishedAt',
    )
    return response.get('articles', [])

def _fetch_cryptopanic_news(api_key: str, query: str) -> list:
    """
    Fetches news articles from CryptoPanic API.
    """
    print("Fetching news from CryptoPanic...")
    url = f"https://cryptopanic.com/api/v2/posts/?auth_token={api_key}&currencies={query}&public=true"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    articles = []
    for item in data.get('results', []):
        articles.append({
            'publishedAt': item.get('created_at'),
            'title': item.get('title'),
            'description': item.get('title'),
            'url': item.get('url'),
            'source': {'name': item.get('source', {}).get('title')}
        })
    return articles

def fetch_news(api_key: str, query: str, from_date: str, to_date: str, output_path: str, source: str = 'newsapi'):
    """
    Fetches news articles from the specified source.
    """
    if source == 'cryptopanic':
        articles = _fetch_cryptopanic_news(api_key, query)
    elif source == 'newsapi':
        articles = _fetch_newsapi_news(api_key, query, from_date, to_date)
    else:
        raise ValueError(f"Unknown news source: {source}")

    if not articles:
        print(f"Warning: Fetched 0 articles from {source}. No data will be written.")
        return

    output_data = {'articles': articles}
    try:
        absolute_output_path = os.path.abspath(output_path)
        print(f"Attempting to write {len(articles)} articles to: {absolute_output_path}")
        os.makedirs(os.path.dirname(absolute_output_path), exist_ok=True)
        with open(absolute_output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved data to {absolute_output_path}")
    except IOError as e:
        print(f"\n--- FILE WRITE ERROR ---\n")
        print(f"An I/O error occurred while trying to write to the file: {e}")
        print(f"Please check if you have write permissions for the directory: {os.path.dirname(absolute_output_path)}")
        print(f"------------------------\n")
    except Exception as e:
        print(f"\n--- UNEXPECTED ERROR ---\n")
        print(f"An unexpected error occurred during file writing: {e}")
        print(f"------------------------\n")

def _load_config_for_main():
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')
    if not os.path.exists(config_path):
        config_path = 'config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

if __name__ == '__main__':
    config = _load_config_for_main()
    news_config = config['news']
    
    SOURCE = news_config.get('source', 'newsapi')
    QUERY = news_config['query']
    FROM_DATE = str(news_config['from_date'])
    TO_DATE = str(news_config['to_date'])

    api_key = os.getenv("NEWS_API_KEY") if SOURCE == 'newsapi' else os.getenv("CRYPTOPANIC_API_KEY")

    if not api_key:
        print(f"API key for {SOURCE} not found in .env file. Skipping.")
    else:
        print(f"\n--- Running {SOURCE} Fetcher Example from Config ---")
        script_dir = os.path.dirname(__file__)
        data_dir = os.path.join(script_dir, '..', 'data')
        raw_news_dir = os.path.join(data_dir, 'raw_news')

        OUTPUT_DIR = raw_news_dir
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"{SOURCE}_{QUERY}_{FROM_DATE}_{TO_DATE}.json")
        fetch_news(api_key, QUERY, FROM_DATE, TO_DATE, OUTPUT_PATH, source=SOURCE)

