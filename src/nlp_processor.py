import pandas as pd
import nltk
import spacy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os

# --- Download necessary NLTK and spaCy models ---
def download_nlp_models():
    """Downloads the VADER lexicon for NLTK and the spaCy model."""
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except nltk.downloader.DownloadError:
        print("Downloading NLTK VADER lexicon...")
        nltk.download('vader_lexicon')
    
    try:
        spacy.load('en_core_web_sm')
    except OSError:
        print("Downloading spaCy model 'en_core_web_sm'...")
        spacy.cli.download('en_core_web_sm')

# --- NLP Processing Functions ---
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
    and saves the enriched data to a new CSV file.
    """
    # Download models first
    download_nlp_models()

    # Load NLP models
    sid = SentimentIntensityAnalyzer()
    nlp = spacy.load('en_core_web_sm')

    # Load cleaned data
    df = pd.read_csv(input_path)

    # --- Apply NLP functions ---
    # 1. Sentiment Analysis
    df['sentiment_score'] = df['content_cleaned'].apply(lambda text: analyze_sentiment(text, sid))

    # 2. Named Entity Recognition
    df['entities'] = df['content_cleaned'].apply(lambda text: extract_entities(text, nlp))

    # Save the processed data
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Successfully processed NLP features and saved to {output_path}")

if __name__ == '__main__':
    # Example usage
    QUERY = 'cryptocurrency'
    FROM_DATE = '2024-06-01'
    TO_DATE = '2024-07-01'
    
    INPUT_DIR = os.path.join('..', '..', 'data', 'processed_news')
    INPUT_PATH = os.path.join(INPUT_DIR, f"cleaned_{QUERY}_{FROM_DATE}_{TO_DATE}.csv")

    OUTPUT_DIR = os.path.join('..', '..', 'data', 'processed_news')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"features_{QUERY}_{FROM_DATE}_{TO_DATE}.csv")

    if not os.path.exists(INPUT_PATH):
        print(f"Input file not found: {INPUT_PATH}")
        print("Please run the text_cleaner.py script first.")
    else:
        process_nlp_features(INPUT_PATH, OUTPUT_PATH)
