# src/scraper.py

import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("CRYPTOPANIC_API_KEY")
print(f"API_KEY loaded: {API_KEY}")

def fetch_crypto_news():
    url = "https://cryptopanic.com/api/"
    params = {
        "auth_token": API_KEY,
        "filter": "news",
        "currencies": "BTC",
        "public": "true"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching news: {response.status_code}")
    
    data = response.json()["results"]
    news_list = []
    for item in data:
        news_list.append({
            "published_at": item.get("published_at"),
            "title": item.get("title"),
            "source": item.get("source", {}).get("title"),
            "url": item.get("url")
        })
    
    df = pd.DataFrame(news_list)
    df["published_at"] = pd.to_datetime(df["published_at"])
    return df

if __name__ == "__main__":
    df = fetch_crypto_news()
    print(df.head())
    df.to_csv("data/raw/crypto_news.csv", index=False)
