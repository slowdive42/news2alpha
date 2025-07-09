import os
import yaml
import pandas as pd

def align_features_with_market_data(
    news_features_path: str, 
    market_data_path: str, 
    output_path: str
):
    """
    Aligns aggregated NLP features from news with market data.
    """
    news_df = pd.read_csv(news_features_path)
    market_df = pd.read_csv(market_data_path)

    news_df['publishedAt'] = pd.to_datetime(news_df['publishedAt'])
    news_df.set_index('publishedAt', inplace=True)

    daily_sentiment = news_df['sentiment_score'].resample('D').mean()
    daily_news_count = news_df['sentiment_score'].resample('D').count()

    aggregated_df = pd.DataFrame({
        'sentiment_mean': daily_sentiment,
        'news_count': daily_news_count
    })

    market_df['Date'] = pd.to_datetime(market_df['Date'])
    market_df.set_index('Date', inplace=True)

    final_df = market_df.join(aggregated_df, how='left')
    final_df['sentiment_mean'].fillna(0, inplace=True)
    final_df['news_count'].fillna(0, inplace=True)

    final_df.to_csv(output_path)
    print(f"Successfully aligned features and saved to {output_path}")

def _load_config_for_main():
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')
    if not os.path.exists(config_path):
        config_path = 'config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

if __name__ == '__main__':
    config = _load_config_for_main()
    news_config = config['news']
    market_config = config['market']

    QUERY = news_config['query']
    FROM_DATE = str(news_config['from_date'])
    TO_DATE = str(news_config['to_date'])
    SYMBOL = market_config['symbol']
    INTERVAL = market_config['interval']

    NEWS_FEATURES_PATH = os.path.join(
        '..', '..', 'data', 'processed_news',
        f"features_{QUERY}_{FROM_DATE}_{TO_DATE}.csv"
    )
    MARKET_DATA_PATH = os.path.join(
        '..', '..', 'data', 'market_data',
        f"{SYMBOL}_{INTERVAL}_{FROM_DATE}_{TO_DATE}.csv"
    )

    OUTPUT_DIR = os.path.join('..', '..', 'data', 'final_features')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"final_{SYMBOL}_{FROM_DATE}_{TO_DATE}.csv")

    if not os.path.exists(NEWS_FEATURES_PATH) or not os.path.exists(MARKET_DATA_PATH):
        print("Input files not found. Please run previous scripts first:")
        print(f"- Features: {NEWS_FEATURES_PATH}")
        print(f"- Market: {MARKET_DATA_PATH}")
    else:
        align_features_with_market_data(NEWS_FEATURES_PATH, MARKET_DATA_PATH, OUTPUT_PATH)
