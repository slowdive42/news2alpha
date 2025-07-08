import pytest
import pandas as pd
from src.market_data_fetcher import fetch_market_data

@pytest.fixture
def temp_output_dir(tmp_path):
    return tmp_path

def test_fetch_market_data_success(mocker, temp_output_dir):
    """Test that fetch_market_data correctly calls yfinance and saves the data."""
    # Arrange: Mock yfinance.download
    mock_download = mocker.patch('yfinance.download')
    mock_data = pd.DataFrame({
        'Open': [100], 'High': [110], 'Low': [90], 'Close': [105]
    })
    mock_download.return_value = mock_data

    output_path = temp_output_dir / "test_market_data.csv"

    # Act: Call the function
    fetch_market_data(
        ticker='TEST-TICKER',
        start_date='2024-01-01',
        end_date='2024-01-02',
        output_path=str(output_path)
    )

    # Assert: Check that the download function was called and the file was written
    mock_download.assert_called_once_with(
        'TEST-TICKER', start='2024-01-01', end='2024-01-02'
    )
    
    assert output_path.exists()
    df = pd.read_csv(output_path)
    assert df['Close'].iloc[0] == 105
