import yfinance as yf
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

def fetch_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Fetches historical stock data for a given ticker."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    if hist.empty:
        raise ValueError(f"No data found for ticker: {ticker}")
    print(f"Successfully fetched price history for {ticker}.")
    return hist

def fetch_news(ticker: str, max_items: int = 5) -> list[dict]:
    """Fetches news articles from Google News RSS and Yahoo Finance."""
    articles = []
    sources = {
        "google": f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en",
        "yahoo": f"https://finance.yahoo.com/quote/{ticker}"
    }

    # 1. Google News RSS
    try:
        response = requests.get(sources["google"])
        root = ET.fromstring(response.content)
        for item in root.findall('.//item')[:max_items]:
            articles.append({
                "title": item.find('title').text,
                "link": item.find('link').text,
                "source": "Google News"
            })
    except Exception as e:
        print(f"Could not fetch Google News for {ticker}: {e}")

    # 2. Yahoo Finance Scraper
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(sources["yahoo"], headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find the news list (selector might need updating if Yahoo changes their site)
        news_list = soup.find_all('li', class_='js-stream-content', limit=max_items)
        for item in news_list:
            link_tag = item.find('a')
            if link_tag and link_tag.has_attr('href'):
                articles.append({
                    "title": link_tag.get_text(strip=True),
                    "link": f"https://finance.yahoo.com{link_tag['href']}",
                    "source": "Yahoo Finance"
                })
    except Exception as e:
        print(f"Could not fetch Yahoo Finance news for {ticker}: {e}")

    print(f"Fetched {len(articles)} articles for {ticker}.")
    return articles
