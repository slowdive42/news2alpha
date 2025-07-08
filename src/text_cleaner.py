import re
import pandas as pd

def clean_text(text: str) -> str:
    """
    Cleans a single text string by removing HTML tags, non-alphanumeric characters,
    and converting to lowercase.

    Args:
        text (str): The input text string.

    Returns:
        str: The cleaned text string.
    """
    if not isinstance(text, str):
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace
    text = " ".join(text.split())
    return text

def clean_news_data(input_path: str, output_path: str):
    """
    Reads raw news data from a JSON file, cleans the 'title' and 'content'
    fields, and saves the result to a CSV file.

    Args:
        input_path (str): Path to the raw news JSON file.
        output_path (str): Path to save the cleaned news CSV file.
    """
    try:
        # Load the raw news data
        df = pd.read_json(input_path)
        articles_df = pd.json_normalize(df['articles'])
    except Exception as e:
        print(f"Error reading or parsing JSON file: {e}")
        return

    # Clean the text fields
    articles_df['title_cleaned'] = articles_df['title'].apply(clean_text)
    articles_df['content_cleaned'] = articles_df['content'].apply(clean_text)

    # Select and save relevant columns
    cleaned_df = articles_df[['publishedAt', 'title', 'title_cleaned', 'content', 'content_cleaned', 'url']]
    cleaned_df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Successfully cleaned news data and saved to {output_path}")

if __name__ == '__main__':
    import os

    # Example usage
    QUERY = 'cryptocurrency'
    FROM_DATE = '2024-06-01'
    TO_DATE = '2024-07-01'
    
    INPUT_DIR = os.path.join('..', '..', 'data', 'raw_news')
    INPUT_PATH = os.path.join(INPUT_DIR, f"{QUERY}_{FROM_DATE}_{TO_DATE}.json")

    OUTPUT_DIR = os.path.join('..', '..', 'data', 'processed_news')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"cleaned_{QUERY}_{FROM_DATE}_{TO_DATE}.csv")

    if not os.path.exists(INPUT_PATH):
        print(f"Input file not found: {INPUT_PATH}")
        print("Please run the news_fetcher.py script first.")
    else:
        clean_news_data(INPUT_PATH, OUTPUT_PATH)
