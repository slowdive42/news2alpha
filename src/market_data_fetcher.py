import os
import yaml
import pandas as pd
import ccxt
from datetime import datetime, timezone

def fetch_market_data(symbol: str, interval: str, start_str: str, end_str: str, output_path: str):
    """
    Fetches historical market data from Binance using CCXT and saves it in a format
    compatible with the rest of the pipeline.

    Args:
        symbol (str): The trading pair symbol in CCXT format (e.g., 'BTC/USDT').
        interval (str): The K-line interval (e.g., '1m', '1d').
        start_str (str): The start date (YYYY-MM-DD).
        end_str (str): The end date (YYYY-MM-DD).
        output_path (str): The path to save the market data CSV file.
    """
    exchange_params = {}
    proxies = {}

    if 'HTTP_PROXY' in os.environ:
        proxies['http'] = os.environ['HTTP_PROXY']
    if 'HTTPS_PROXY' in os.environ:
        proxies['https'] = os.environ['HTTPS_PROXY']

    if proxies:
        exchange_params['proxies'] = proxies
        print(f"Using proxies: {proxies}")

    exchange = ccxt.binance(exchange_params)
    print(f"Fetching {symbol} data for interval {interval} from Binance using CCXT...")

    # Convert dates to milliseconds
    since = int(datetime.strptime(start_str, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp() * 1000)
    end_msec = int(datetime.strptime(end_str, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp() * 1000)

    all_klines = []
    while since < end_msec:
        try:
            klines = exchange.fetch_ohlcv(symbol, timeframe=interval, since=since)
            if not klines:
                break # No more data
            all_klines.extend(klines)
            since = klines[-1][0] + exchange.parse_timeframe(interval) * 1000 # Move to the next timeframe
        except Exception as e:
            print(f"An error occurred while fetching data: {e}")
            break

    if not all_klines:
        print("No data found for the specified parameters.")
        return

    # Process into a pandas DataFrame
    data = pd.DataFrame(all_klines, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    data['Date'] = pd.to_datetime(data['timestamp'], unit='ms').dt.tz_localize('UTC') # Localize to UTC
    data.set_index('Date', inplace=True)

    # Select and reorder columns for pipeline compatibility
    output_df = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()

    # Save the data
    output_df.to_csv(output_path)
    print(f"Successfully saved market data to {output_path}")

def _load_config_for_main():
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')
    if not os.path.exists(config_path):
        config_path = 'config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

if __name__ == '__main__':
    config = _load_config_for_main()
    market_config = config['market']
    news_config = config['news']

    # CCXT uses '/' in symbols, e.g., BTC/USDT
    SYMBOL = market_config['symbol'].replace('USDT', '/USDT') 
    INTERVAL = market_config['interval']
    FROM_DATE = news_config['from_date']
    TO_DATE = news_config['to_date']

    OUTPUT_DIR = os.path.join('..', '..', 'data', 'market_data')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"{market_config['symbol']}_{INTERVAL}_{FROM_DATE}_{TO_DATE}.csv")

    fetch_market_data(SYMBOL, INTERVAL, FROM_DATE, TO_DATE, OUTPUT_PATH)

