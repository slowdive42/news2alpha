import pytest
import pandas as pd
from src.nlp_processor import process_nlp_features, download_nlp_models

@pytest.fixture
def cleaned_news_file(tmp_path):
    """Create a dummy cleaned news CSV file for testing."""
    data = {
        'publishedAt': ['2024-01-01T12:00:00Z'],
        'title': ['Test Title'],
        'title_cleaned': ['test title'],
        'content': ['Positive news about crypto.'],
        'content_cleaned': ['positive news about crypto'],
        'url': ['http://example.com']
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "cleaned_news.csv"
    df.to_csv(file_path, index=False)
    return str(file_path)

# Mock the download function to prevent actual downloads during tests
@pytest.fixture(autouse=True)
def mock_downloads(mocker):
    mocker.patch('src.nlp_processor.download_nlp_models', return_value=None)

def test_process_nlp_features(mocker, cleaned_news_file, tmp_path):
    """Test the NLP processing workflow with mocked models."""
    # Arrange
    # Mock NLTK Sentiment Analyzer
    mock_sid = mocker.patch('nltk.sentiment.vader.SentimentIntensityAnalyzer').return_value
    mock_sid.polarity_scores.return_value = {'compound': 0.85}

    # Mock spaCy
    mock_spacy_load = mocker.patch('spacy.load')
    mock_nlp = mocker.MagicMock()
    mock_doc = mocker.MagicMock()
    mock_ent = mocker.MagicMock()
    mock_ent.text = 'crypto'
    mock_ent.label_ = 'MONEY'
    mock_doc.ents = [mock_ent]
    mock_nlp.return_value = mock_doc
    mock_spacy_load.return_value = mock_nlp

    output_path = tmp_path / "features.csv"

    # Act
    process_nlp_features(cleaned_news_file, str(output_path))

    # Assert
    assert output_path.exists()
    df = pd.read_csv(output_path)

    assert 'sentiment_score' in df.columns
    assert 'entities' in df.columns
    assert df['sentiment_score'].iloc[0] == 0.85
    assert "('crypto', 'MONEY')" in df['entities'].iloc[0]
