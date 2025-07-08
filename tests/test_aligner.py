import pytest
import pandas as pd
from src.aligner import align_features_with_market_data

@pytest.fixture
def nlp_features_file(tmp_path):
    """Create a dummy NLP features CSV file."""
    data = {
        'publishedAt': ['2024-01-01T10:00:00Z', '2024-01-01T14:00:00Z', '2024-01-02T11:00:00Z'],
        'sentiment_score': [0.5, -0.1, 0.9],
        'entities': ["[ ('BTC', 'ORG') ]", "[]", "[ ('ETH', 'ORG') ]"]
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "features.csv"
    df.to_csv(file_path, index=False)
    return str(file_path)

@pytest.fixture
def market_data_file(tmp_path):
    """Create a dummy market data CSV file."""
    data = {
        'Date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
        'Close': [50000, 51000, 50500]
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "market.csv"
    df.to_csv(file_path, index=False)
    return str(file_path)

def test_align_features_with_market_data(nlp_features_file, market_data_file, tmp_path):
    """Test the alignment of NLP features with market data."""
    # Arrange
    output_path = tmp_path / "final_features.csv"

    # Act
    align_features_with_market_data(nlp_features_file, market_data_file, str(output_path))

    # Assert
    assert output_path.exists()
    df = pd.read_csv(output_path, index_col='Date', parse_dates=True)

    # Check columns
    assert 'sentiment_mean' in df.columns
    assert 'news_count' in df.columns
    assert 'Close' in df.columns

    # Check values for 2024-01-01 (mean of 0.5 and -0.1 is 0.2)
    assert df.loc['2024-01-01']['sentiment_mean'] == pytest.approx(0.2)
    assert df.loc['2024-01-01']['news_count'] == 2

    # Check values for 2024-01-02
    assert df.loc['2024-01-02']['sentiment_mean'] == 0.9
    assert df.loc['2024-01-02']['news_count'] == 1

    # Check values for 2024-01-03 (day with no news)
    assert df.loc['2024-01-03']['sentiment_mean'] == 0.0
    assert df.loc['2024-01-03']['news_count'] == 0
