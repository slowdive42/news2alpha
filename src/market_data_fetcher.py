from binance.client import Client
import pandas as pd
import os
from datetime import datetime

# Replace with your actual API key and secret from environment variables or a config file
# For security, it's recommended to use environment variables.
# BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
# BINANCE_API_SECRET = os.environ.get('BINANCE_API_SECRET')

# For demonstration purposes, you can hardcode them, but NOT recommended for production.
# client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
# If you don't have an API key and secret, you can use the testnet or public endpoints.
# For public data, you might not need API key/secret, but for historical klines, it's better to have them.
client = Client("", "") # Using empty strings for public access, replace with your keys if needed

def fetch_market_data(symbol: str, interval: str, start_str: str, end_str: str, output_path: str):
    """
    Fetches historical market data from Binance for a given symbol and interval.

    Args:
        symbol (str): The trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT').
        interval (str): The K-line interval (e.g., Client.KLINE_INTERVAL_1MINUTE, Client.KLINE_INTERVAL_5MINUTE, Client.KLINE_INTERVAL_1HOUR).
        start_str (str): The start date for the data (e.g., '1 Jan, 2024').
        end_str (str): The end date for the data (e.g., '1 Feb, 2024').
        output_path (str): The path to save the market data (CSV file).
    """
    print(f"Fetching {symbol} {interval} data from Binance...")
    klines = client.get_historical_klines(symbol, interval, start_str, end_str)

    if not klines:
        print(f"No data found for symbol {symbol} with interval {interval} in the specified date range.")
        return

    # Process the klines into a pandas DataFrame
    data = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])

    data['open_time'] = pd.to_datetime(data['open_time'], unit='ms')
    data['close_time'] = pd.to_datetime(data['close_time'], unit='ms')
    data = data.astype({
        'open': float, 'high': float, 'low': float, 'close': float, 'volume': float,
        'quote_asset_volume': float, 'number_of_trades': int,
        'taker_buy_base_asset_volume': float, 'taker_buy_quote_asset_volume': float
    })

    # Set open_time as index
    data.set_index('open_time', inplace=True)

    data.to_csv(output_path)
    print(f"Successfully downloaded market data for {symbol} and saved to {output_path}")

if __name__ == '__main__':
    # This is an example of how to run the fetcher directly
    SYMBOL = 'BTCUSDT'
    INTERVAL = Client.KLINE_INTERVAL_5MINUTE # Example: 5-minute interval
    START_DATE_STR = '1 July, 2024'
    END_DATE_STR = '8 July, 2024'
    OUTPUT_DIR = os.path.join('..', '..', 'data', 'market_data')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"{SYMBOL}_{INTERVAL}_{START_DATE_STR.replace(' ', '_')}_{END_DATE_STR.replace(' ', '_')}.csv")

    fetch_market_data(SYMBOL, INTERVAL, START_DATE_STR, END_DATE_STR, OUTPUT_PATH)
