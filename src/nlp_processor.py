import os
import yaml
import pandas as pd
import nltk
import spacy
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def download_nlp_models():
    """Downloads the VADER lexicon for NLTK and the spaCy model."""
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        print("Downloading vader_lexicon...")
        nltk.download("vader_lexicon")
    try:
        spacy.load('en_core_web_sm')
    except OSError:
        print("Downloading spaCy model 'en_core_web_sm'...")
        spacy.cli.download('en_core_web_sm')

def analyze_sentiment(text: str, sid: SentimentIntensityAnalyzer) -> float:
    """Analyzes the sentiment of a text and returns the compound score."""
    if not isinstance(text, str) or not text.strip():
        return 0.0
    return sid.polarity_scores(text)['compound']

def extract_entities(text: str, nlp_model) -> list:
    """Extracts named entities from a text."""
    if not isinstance(text, str) or not text.strip():
        return []
    doc = nlp_model(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def process_nlp_features(input_path: str, output_path: str):
    """
    Reads cleaned news data, applies sentiment analysis and NER,
    and saves the enriched data.
    """
    download_nlp_models()
    sid = SentimentIntensityAnalyzer()
    nlp = spacy.load('en_core_web_sm')
    df = pd.read_csv(input_path)

    df['sentiment_score'] = df['content_cleaned'].apply(lambda text: analyze_sentiment(text, sid))
    df['entities'] = df['content_cleaned'].apply(lambda text: extract_entities(text, nlp))

    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Successfully processed NLP features and saved to {output_path}")

def _load_config_for_main():
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')
    if not os.path.exists(config_path):
        config_path = 'config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

if __name__ == '__main__':
    config = _load_config_for_main()
    news_config = config['news']

    QUERY = news_config['query']
    FROM_DATE = str(news_config['from_date'])
    TO_DATE = str(news_config['to_date'])

    script_dir = os.path.dirname(__file__)
    data_dir = os.path.join(script_dir, '..', 'data')
    processed_news_dir = os.path.join(data_dir, 'processed_news')

    INPUT_PATH = os.path.join(processed_news_dir, f"cleaned_{QUERY}_{FROM_DATE}_{TO_DATE}.csv")
    OUTPUT_DIR = processed_news_dir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"features_{QUERY}_{FROM_DATE}_{TO_DATE}.csv")

    if not os.path.exists(INPUT_PATH):
        print(f"Input file not found: {INPUT_PATH}")
    else:
        process_nlp_features(INPUT_PATH, OUTPUT_PATH)
