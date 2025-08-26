import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from typing import List, Dict

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0 Safari/537.36"
REQUEST_TIMEOUT = 10

def fetch_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Fetches historical stock data for a given ticker using yfinance."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    if hist is None or hist.empty:
        raise ValueError(f"No data found for ticker: {ticker}")
    # Ensure index is datetime
    try:
        hist.index = pd.to_datetime(hist.index)
    except Exception:
        pass
    print(f"Successfully fetched price history for {ticker}. Rows: {len(hist)}")
    return hist

def fetch_news(ticker: str, max_items: int = 5) -> List[Dict]:
    """Fetches news articles from Google News RSS and Yahoo Finance (best-effort)."""
    articles = []
    sources = {
        "google": f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en",
        "yahoo": f"https://finance.yahoo.com/quote/{ticker}"
    }

    # 1. Google News RSS
    try:
        response = requests.get(sources["google"], headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        for item in root.findall('.//item')[:max_items]:
            title = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            articles.append({
                "title": title,
                "link": link,
                "source": "Google News"
            })
    except Exception as e:
        print(f"Could not fetch Google News for {ticker}: {e}")

    # 2. Yahoo Finance Scraper (best-effort)
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(sources["yahoo"], headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Try a couple of selectors to be resilient
        news_items = soup.select('li.js-stream-content') or soup.select('h3') or []
        count = 0
        for item in news_items:
            if count >= max_items:
                break
            link_tag = item.find('a') if hasattr(item, 'find') else None
            if link_tag and link_tag.has_attr('href'):
                title = link_tag.get_text(strip=True)
                href = link_tag['href']
                if href.startswith('/'):
                    href = f"https://finance.yahoo.com{href}"
                articles.append({
                    "title": title,
                    "link": href,
                    "source": "Yahoo Finance"
                })
                count += 1
    except Exception as e:
        print(f"Could not fetch Yahoo Finance news for {ticker}: {e}")

    print(f"Fetched {len(articles)} articles for {ticker}.")
    return articles
