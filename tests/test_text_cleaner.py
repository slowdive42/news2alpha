import pytest
import pandas as pd
import json
from src.text_cleaner import clean_text, clean_news_data

# --- Test the core clean_text function ---
@pytest.mark.parametrize("input_text, expected_output", [
    ("<p>Hello World!</p>", "hello world"),
    ("  Special chars!! 123...  ", "special chars"),
    ("Another@Example.com with link", "anotherexamplecom with link"),
    (None, ""),
    ("  Multiple   spaces  ", "multiple spaces")
])
def test_clean_text(input_text, expected_output):
    assert clean_text(input_text) == expected_output

# --- Test the file-level cleaning function ---
@pytest.fixture
def raw_news_file(tmp_path):
    """Create a dummy raw news JSON file for testing."""
    data = {
        'articles': [
            {'title': '<b>Clean Title</b>', 'content': 'Some content 123.', 'url': 'url1'},
            {'title': 'Another Title', 'content': None, 'url': 'url2'} # Test with None content
        ]
    }
    file_path = tmp_path / "raw_news.json"
    with open(file_path, 'w') as f:
        json.dump(data, f)
    return str(file_path)

def test_clean_news_data(raw_news_file, tmp_path):
    """Test the complete clean_news_data workflow."""
    # Arrange
    output_path = tmp_path / "cleaned_news.csv"

    # Act
    clean_news_data(raw_news_file, str(output_path))

    # Assert
    assert output_path.exists()
    df = pd.read_csv(output_path)
    
    assert 'title_cleaned' in df.columns
    assert 'content_cleaned' in df.columns
    assert df['title_cleaned'].iloc[0] == "clean title"
    assert df['content_cleaned'].iloc[0] == "some content"
    # Check that None content results in an empty string
    assert df['content_cleaned'].iloc[1] == ""
