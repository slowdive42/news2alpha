import pytest
import pandas as pd
from src.market_data_fetcher import fetch_market_data

@pytest.fixture
def mock_ccxt_exchange(mocker):
    """Mocks the ccxt.binance() exchange and its fetch_ohlcv method."""
    mock_exchange = mocker.patch('ccxt.binance', autospec=True)
    mock_instance = mock_exchange.return_value

    # Simulate fetching in two pages
    mock_page_1 = [
        [1640995200000, 47000, 48000, 46000, 47500, 1000],
        [1641081600000, 47500, 48500, 47000, 48000, 1200]
    ]
    mock_page_2 = [] # Simulate end of data

    # The side_effect allows returning different values on subsequent calls
    mock_instance.fetch_ohlcv.side_effect = [mock_page_1, mock_page_2]
    mock_instance.parse_timeframe.return_value = 86400000 # 1 day in ms
    return mock_instance

def test_fetch_market_data_ccxt_success(mock_ccxt_exchange, tmp_path):
    """Test that fetch_market_data with CCXT correctly fetches and saves data."""
    # Arrange
    output_path = tmp_path / "market_data_ccxt.csv"
    symbol = 'BTC/USDT'
    interval = '1d'
    start_str = '2022-01-01'
    end_str = '2022-01-03'

    # Act
    fetch_market_data(symbol, interval, start_str, end_str, str(output_path))

    # Assert
    # Check that fetch_ohlcv was called (at least once)
    assert mock_ccxt_exchange.fetch_ohlcv.call_count > 0
    # Check the first call's arguments
    mock_ccxt_exchange.fetch_ohlcv.assert_any_call(
        'BTC/USDT', timeframe='1d', since=1640995200000
    )

    # Check that the file was written and has the correct content
    assert output_path.exists()
    df = pd.read_csv(output_path, index_col='Date', parse_dates=True)
    
    assert df.shape[0] == 2
    assert 'Close' in df.columns
    assert df['Close'].iloc[0] == 47500.0
    assert df['Close'].iloc[1] == 48000.0

