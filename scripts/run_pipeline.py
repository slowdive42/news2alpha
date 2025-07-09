import os
import yaml
from dotenv import load_dotenv
from src.news_fetcher import fetch_news
from src.market_data_fetcher import fetch_market_data
from src.text_cleaner import clean_news_data
from src.nlp_processor import process_nlp_features
from src.aligner import align_features_with_market_data

# Load environment variables
load_dotenv()

# --- Configuration Loading ---
def load_config(config_path='config.yaml'):
    """Loads the configuration from a YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    """Runs the entire NLP signal extraction pipeline based on config."""
    # Load configuration
    config = load_config()
    news_config = config['news']
    market_config = config['market']

    # News parameters
    SOURCE = news_config.get('source', 'newsapi')
    QUERY = news_config['query']
    FROM_DATE = str(news_config['from_date'])
    TO_DATE = str(news_config['to_date'])

    # Market parameters
    SYMBOL = market_config['symbol']
    INTERVAL = market_config['interval']

    # --- Path Definitions ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, '..', 'data')

    RAW_NEWS_DIR = os.path.join(DATA_DIR, 'raw_news')
    MARKET_DATA_DIR = os.path.join(DATA_DIR, 'market_data')
    RAW_NEWS_PATH = os.path.join(RAW_NEWS_DIR, f"{SOURCE}_{QUERY}_{FROM_DATE}_{TO_DATE}.json")
    MARKET_DATA_PATH = os.path.join(MARKET_DATA_DIR, f"{SYMBOL}_{INTERVAL}_{FROM_DATE}_{TO_DATE}.csv")

    PROCESSED_NEWS_DIR = os.path.join(DATA_DIR, 'processed_news')
    CLEANED_NEWS_PATH = os.path.join(PROCESSED_NEWS_DIR, f"cleaned_{QUERY}_{FROM_DATE}_{TO_DATE}.csv")
    FEATURES_PATH = os.path.join(PROCESSED_NEWS_DIR, f"features_{QUERY}_{FROM_DATE}_{TO_DATE}.csv")

    FINAL_FEATURES_DIR = os.path.join(DATA_DIR, 'final_features')
    FINAL_OUTPUT_PATH = os.path.join(FINAL_FEATURES_DIR, f"final_{SYMBOL}_{FROM_DATE}_{TO_DATE}.csv")

    print("--- Starting News2Alpha Pipeline ---")
    print(f"News Config: Source='{SOURCE}', Query='{QUERY}'")
    print(f"Market Config: Symbol='{SYMBOL}', Interval='{INTERVAL}'")
    print(f"Date Range: {FROM_DATE} to {TO_DATE}")

    # Create directories if they don't exist
    for path in [RAW_NEWS_DIR, MARKET_DATA_DIR, PROCESSED_NEWS_DIR, FINAL_FEATURES_DIR]:
        os.makedirs(path, exist_ok=True)

    # --- Step 1: Data Ingestion ---
    print(f"\nStep 1.1: Fetching news from {SOURCE}...")
    if SOURCE == 'cryptopanic':
        api_key = os.getenv("CRYPTOPANIC_API_KEY")
        if not api_key:
            raise ValueError("CRYPTOPANIC_API_KEY not found in .env file. Please add it.")
    elif SOURCE == 'newsapi':
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            raise ValueError("NEWS_API_KEY not found in .env file. Please add it.")
    else:
        raise ValueError(f"Unknown news source in config: {SOURCE}")
    fetch_news(api_key, QUERY, FROM_DATE, TO_DATE, RAW_NEWS_PATH, source=SOURCE)

    print("\nStep 1.2: Fetching market data...")
    fetch_market_data(SYMBOL, INTERVAL, FROM_DATE, TO_DATE, MARKET_DATA_PATH)

    # --- Step 2: Feature Engineering ---
    print("\nStep 2.1: Cleaning news data...")
    clean_news_data(RAW_NEWS_PATH, CLEANED_NEWS_PATH)

    print("\nStep 2.2: Processing NLP features...")
    process_nlp_features(CLEANED_NEWS_PATH, FEATURES_PATH)

    # --- Step 3: Signal Generation ---
    print("\nStep 3.1: Aligning features with market data...")
    align_features_with_market_data(FEATURES_PATH, MARKET_DATA_PATH, FINAL_OUTPUT_PATH)

    print("\n--- Pipeline Finished Successfully! ---")
    print(f"Final feature table saved to: {FINAL_OUTPUT_PATH}")

if __name__ == '__main__':
    main()

