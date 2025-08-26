import os
from groq import Groq
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def summarize_with_groq(client: Groq, text: str) -> str:
    """Uses Groq API to summarize a given text."""
    if not text:
        return "No content to summarize."
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
            model="llama3-8b-8192", # Fast and capable model
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error summarizing with Groq: {e}")
        return "Summarization failed."

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
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    processed = []

    for article in articles:
        summary = summarize_with_groq(client, article['title'])
        sentiment = get_sentiment(summary)

        processed.append({
            "headline": article['title'],
            "summary": summary,
            "sentiment_score": sentiment['compound'],
            "sentiment_label": sentiment['label'],
            "link": article['link'],
            "source": article['source']
        })
    print(f"Processed {len(processed)} articles with Groq and VADER.")
    return processed
