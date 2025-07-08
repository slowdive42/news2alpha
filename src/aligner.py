import pandas as pd
import os

def align_features_with_market_data(
    news_features_path: str, 
    market_data_path: str, 
    output_path: str
):
    """
    Aligns aggregated NLP features from news with market data.

    Args:
        news_features_path (str): Path to the CSV with NLP features.
        market_data_path (str): Path to the market data CSV.
        output_path (str): Path to save the final aligned feature table.
    """
    # Load data
    news_df = pd.read_csv(news_features_path)
    market_df = pd.read_csv(market_data_path)

    # --- Prepare News Data ---
    # Convert 'publishedAt' to datetime and set as index
    news_df['publishedAt'] = pd.to_datetime(news_df['publishedAt'])
    news_df.set_index('publishedAt', inplace=True)

    # --- Aggregate News Features Daily ---
    # We can customize the aggregation logic here. For now, we'll use mean sentiment.
    daily_sentiment = news_df['sentiment_score'].resample('D').mean()
    daily_news_count = news_df['sentiment_score'].resample('D').count()

    # Combine aggregated features into a single DataFrame
    aggregated_df = pd.DataFrame({
        'sentiment_mean': daily_sentiment,
        'news_count': daily_news_count
    })

    # --- Prepare Market Data ---
    # Convert 'Date' to datetime and set as index
    market_df['Date'] = pd.to_datetime(market_df['Date'])
    market_df.set_index('Date', inplace=True)

    # --- Merge DataFrames ---
    # Merge the daily aggregated news features with the market data
    final_df = market_df.join(aggregated_df, how='left')

    # Fill missing sentiment values (days with no news) with 0
    final_df['sentiment_mean'].fillna(0, inplace=True)
    final_df['news_count'].fillna(0, inplace=True)

    # Save the final feature table
    final_df.to_csv(output_path)
    print(f"Successfully aligned features and saved to {output_path}")

if __name__ == '__main__':
    # Example usage
    QUERY = 'cryptocurrency'
    TICKER = 'BTC-USD'
    FROM_DATE = '2024-06-01'
    TO_DATE = '2024-07-01'

    # Input paths
    NEWS_FEATURES_PATH = os.path.join(
        '..', '..', 'data', 'processed_news',
        f"features_{QUERY}_{FROM_DATE}_{TO_DATE}.csv"
    )
    MARKET_DATA_PATH = os.path.join(
        '..', '..', 'data', 'market_data',
        f"{TICKER}_{START_DATE}_{END_DATE}.csv"
    )

    # Output path
    OUTPUT_DIR = os.path.join('..', '..', 'data', 'final_features')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"final_{TICKER}_{FROM_DATE}_{TO_DATE}.csv")

    # Check if input files exist
    if not os.path.exists(NEWS_FEATURES_PATH) or not os.path.exists(MARKET_DATA_PATH):
        print("Input files not found. Please run previous scripts first:")
        print(f"- {NEWS_FEATURES_PATH}")
        print(f"- {MARKET_DATA_PATH}")
    else:
        align_features_with_market_data(NEWS_FEATURES_PATH, MARKET_DATA_PATH, OUTPUT_PATH)
