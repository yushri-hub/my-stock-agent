import os
try:
    from groq import Groq
except Exception:
    Groq = None
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def summarize_with_groq(client, text: str) -> str:
    """Uses Groq API to summarize a given text. Returns fallback text on failure or missing client."""
    if not text:
        return "No content to summarize."
    if client is None:
        # Fallback summarization: return the first sentence or trimmed headline
        return text if len(text) < 300 else text[:300] + '...'
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial news analyst. Summarize the following article for an investor in 2-3 concise sentences. Focus on the key facts, figures, and potential market impact. Ignore boilerplate text."
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error summarizing with Groq: {e}")
        return text if len(text) < 300 else text[:300] + '...'

def get_sentiment(text: str) -> dict:
    """Gets sentiment score using VADER."""
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    # Classify sentiment based on compound score
    if sentiment['compound'] >= 0.05:
        sentiment['label'] = 'Positive'
    elif sentiment['compound'] <= -0.05:
        sentiment['label'] = 'Negative'
    else:
        sentiment['label'] = 'Neutral'
    return sentiment

def process_articles(articles: list[dict]) -> list[dict]:
    """Summarizes and analyzes sentiment for a list of articles."""
    groq_key = os.environ.get("GROQ_API_KEY")
    client = Groq(api_key=groq_key) if (Groq is not None and groq_key) else None
    processed = []

    for article in articles:
        summary = summarize_with_groq(client, article.get('title') or article.get('headline') or '')
        sentiment = get_sentiment(summary)

        processed.append({
            "headline": article.get('title') or article.get('headline') or '',
            "summary": summary,
            "sentiment_score": sentiment['compound'],
            "sentiment_label": sentiment['label'],
            "link": article.get('link', ''),
            "source": article.get('source', '')
        })
    print(f"Processed {len(processed)} articles with Groq (if available) and VADER.")
    return processed
