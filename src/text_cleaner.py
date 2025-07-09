import os
import re
import yaml
import pandas as pd

def clean_text(text: str) -> str:
    """
    Cleans a single text string by removing HTML tags, non-alphanumeric characters,
    and converting to lowercase.
    """
    if not isinstance(text, str):
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    text = " ".join(text.split())
    return text

def clean_news_data(input_path: str, output_path: str):
    """
    Reads raw news data from a JSON file, cleans the text content,
    and saves the result to a CSV file.
    """
    try:
        df = pd.read_json(input_path)
        if 'articles' not in df:
            print(f"Error: JSON file {input_path} does not have an 'articles' key.")
            return
        articles_df = pd.json_normalize(df['articles'])
    except Exception as e:
        print(f"Error reading or parsing JSON file: {e}")
        return

    # The content field might be named 'description' or 'content'
    content_col = 'description' if 'description' in articles_df.columns else 'content'
    if content_col not in articles_df.columns:
        print(f"Error: Neither 'description' nor 'content' column found in the input data.")
        return

    articles_df['title_cleaned'] = articles_df['title'].apply(clean_text)
    articles_df['content_cleaned'] = articles_df[content_col].apply(clean_text)

    cleaned_df = articles_df[['publishedAt', 'title', 'title_cleaned', content_col, 'content_cleaned', 'url']]
    cleaned_df.rename(columns={content_col: 'content'}, inplace=True)
    
    cleaned_df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Successfully cleaned news data and saved to {output_path}")

def _load_config_for_main():
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')
    if not os.path.exists(config_path):
        config_path = 'config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

if __name__ == '__main__':
    config = _load_config_for_main()
    news_config = config['news']

    SOURCE = news_config.get('source', 'newsapi')
    QUERY = news_config['query']
    FROM_DATE = str(news_config['from_date'])
    TO_DATE = str(news_config['to_date'])

    INPUT_PATH = os.path.join('..', '..', 'data', 'raw_news', f"{SOURCE}_{QUERY}_{FROM_DATE}_{TO_DATE}.json")
    OUTPUT_DIR = os.path.join('..', '..', 'data', 'processed_news')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"cleaned_{QUERY}_{FROM_DATE}_{TO_DATE}.csv")

    if not os.path.exists(INPUT_PATH):
        print(f"Input file not found: {INPUT_PATH}")
        print("Please run the news_fetcher.py script first.")
    else:
        clean_news_data(INPUT_PATH, OUTPUT_PATH)
