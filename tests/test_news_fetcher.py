import pytest
import json
import pytest_mock # Added for mocker fixture
from src.news_fetcher import fetch_news

@pytest.fixture
def temp_output_dir(tmp_path):
    return tmp_path

def test_fetch_news_newsapi_success(mocker, temp_output_dir):
    """Test fetch_news with source='newsapi'."""
    # Arrange
    mock_api_client = mocker.patch('newsapi.NewsApiClient')
    mock_instance = mock_api_client.return_value
    mock_instance.get_everything.return_value = {
        'articles': [{'title': 'Test Article', 'description': 'Test content.'}]
    }
    output_path = temp_output_dir / "test_news_api.json"

    # Act
    fetch_news(
        api_key='test_key',
        query='test_query',
        from_date='2024-01-01',
        to_date='2024-01-02',
        output_path=str(output_path),
        source='newsapi'
    )

    # Assert
    mock_instance.get_everything.assert_called_once()
    assert output_path.exists()
    with open(output_path, 'r') as f:
        data = json.load(f)
    assert data['articles'][0]['title'] == 'Test Article'

def test_fetch_news_cryptopanic_success(mocker, temp_output_dir):
    """Test fetch_news with source='cryptopanic'."""
    # Arrange
    mock_requests_get = mocker.patch('requests.get')
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = {
        'results': [{
            'title': 'CryptoPanic Article',
            'created_at': '2024-01-01T12:00:00Z',
            'url': 'http://cp.com/1',
            'source': {'title': 'CryptoPanic Source'}
        }]
    }
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response
    output_path = temp_output_dir / "test_cryptopanic.json"

    # Act
    fetch_news(
        api_key='cp_key',
        query='BTC',
        from_date='', # Ignored by this fetcher
        to_date='',   # Ignored by this fetcher
        output_path=str(output_path),
        source='cryptopanic'
    )

    # Assert
    mock_requests_get.assert_called_once()
    assert output_path.exists()
    with open(output_path, 'r') as f:
        data = json.load(f)
    assert data['articles'][0]['title'] == 'CryptoPanic Article'
    assert data['articles'][0]['description'] == 'CryptoPanic Article' # Check normalization
