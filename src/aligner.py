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
    if news_df['publishedAt'].dt.tz is None:
        news_df['publishedAt'] = news_df['publishedAt'].dt.tz_localize('UTC')
    else:
        news_df['publishedAt'] = news_df['publishedAt'].dt.tz_convert('UTC')
    news_df.set_index('publishedAt', inplace=True)
    print("\n--- news_df after set_index ---")
    print(f"Min Date: {news_df.index.min()}")
    print(f"Max Date: {news_df.index.max()}")
    print(f"Shape: {news_df.shape}")
    print(news_df.head())

    daily_sentiment = news_df['sentiment_score'].resample('D').mean()
    daily_news_count = news_df['sentiment_score'].resample('D').count()

    aggregated_df = pd.DataFrame({
        'sentiment_mean': daily_sentiment,
        'news_count': daily_news_count
    })
    print("\n--- aggregated_df ---")
    print(f"Min Date: {aggregated_df.index.min()}")
    print(f"Max Date: {aggregated_df.index.max()}")
    print(f"Shape: {aggregated_df.shape}")
    print(aggregated_df.head())

    market_df['Date'] = pd.to_datetime(market_df['Date'])
    if market_df['Date'].dt.tz is None:
        market_df['Date'] = market_df['Date'].dt.tz_localize('UTC')
    else:
        market_df['Date'] = market_df['Date'].dt.tz_convert('UTC')
    market_df.set_index('Date', inplace=True)
    print("\n--- market_df after set_index ---")
    print(f"Min Date: {market_df.index.min()}")
    print(f"Max Date: {market_df.index.max()}")
    print(f"Shape: {market_df.shape}")
    print(market_df.head())

    final_df = market_df.join(aggregated_df, how='left')
    print("\n--- final_df null counts before fillna ---")
    print(final_df.isnull().sum())
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

    script_dir = os.path.dirname(__file__)
    data_dir = os.path.join(script_dir,  '..', 'data')
    processed_news_dir = os.path.join(data_dir, 'processed_news')
    market_data_dir = os.path.join(data_dir, 'market_data')
    final_features_dir = os.path.join(data_dir, 'final_features')

    NEWS_FEATURES_PATH = os.path.join(processed_news_dir,
        f"features_{QUERY}_{FROM_DATE}_{TO_DATE}.csv"
    )
    MARKET_DATA_PATH = os.path.join(market_data_dir,
        f"{SYMBOL}_{INTERVAL}_{FROM_DATE}_{TO_DATE}.csv"
    )

    OUTPUT_DIR = final_features_dir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"final_{SYMBOL}_{FROM_DATE}_{TO_DATE}.csv")

    if not os.path.exists(NEWS_FEATURES_PATH) or not os.path.exists(MARKET_DATA_PATH):
        print("Input files not found. Please run previous scripts first:")
        print(f"- Features: {NEWS_FEATURES_PATH}")
        print(f"- Market: {MARKET_DATA_PATH}")
    else:
        align_features_with_market_data(NEWS_FEATURES_PATH, MARKET_DATA_PATH, OUTPUT_PATH)
