import pytest
import json
from src.news_fetcher import fetch_news

# A fixture to create a temporary directory for test outputs
@pytest.fixture
def temp_output_dir(tmp_path):
    return tmp_path

def test_fetch_news_success(mocker, temp_output_dir):
    """Test that fetch_news correctly calls the API and saves the data."""
    # Arrange: Mock the NewsApiClient
    mock_api_client = mocker.patch('newsapi.NewsApiClient')
    mock_instance = mock_api_client.return_value
    mock_instance.get_everything.return_value = {
        'status': 'ok',
        'totalResults': 1,
        'articles': [{'title': 'Test Article', 'content': 'Test content.'}]
    }

    output_path = temp_output_dir / "test_news.json"

    # Act: Call the function
    fetch_news(
        api_key='test_key',
        query='test_query',
        from_date='2024-01-01',
        to_date='2024-01-02',
        output_path=str(output_path)
    )

    # Assert: Check that the API was called and the file was written
    mock_instance.get_everything.assert_called_once_with(
        q='test_query',
        from_param='2024-01-01',
        to='2024-01-02',
        language='en',
        sort_by='publishedAt'
    )
    
    assert output_path.exists()
    with open(output_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data['articles'][0]['title'] == 'Test Article'
