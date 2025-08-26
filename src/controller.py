import os
from groq import Groq

def decide_action_with_rules(tech_summary: dict, news_summaries: list[dict]) -> tuple[str, str]:
    """Simple rule-based logic to decide an action."""
    reasons = []

    # Technical Rules
    if tech_summary.get('RSI_14', 50) >= 70:
        reasons.append("RSI is overbought (>= 70).")
    if tech_summary.get('RSI_14', 50) <= 30:
        reasons.append("RSI is oversold (<= 30).")
    if tech_summary.get('Close', 0) < tech_summary.get('SMA_50', float('inf')):
        reasons.append("Price crossed below 50-day SMA.")

    # News Rules
    negative_news_count = sum(1 for article in news_summaries if article['sentiment_score'] <= -0.2)
    if negative_news_count >= 2:
        reasons.append(f"High volume of negative news ({negative_news_count} articles).")

    if reasons:
        return "ESCALATE", " & ".join(reasons)

    return "MONITOR", "No significant triggers met."


def get_analyst_opinion(client: Groq, ticker: str, tech_summary: dict, news_summaries: list[dict]) -> str:
    """Uses Groq to provide a high-level opinion on the current situation."""
    prompt_context = f"""
    Analyze the following data for the stock ticker {ticker} and provide a one-paragraph summary for an investor.
    Should I be concerned, optimistic, or just watchful? Explain why briefly.

    **Technical Data:**
    - Close Price: {tech_summary.get('Close', 'N/A'):.2f}
    - 20-Day SMA: {tech_summary.get('SMA_20', 'N/A'):.2f}
    - 50-Day SMA: {tech_summary.get('SMA_50', 'N/A'):.2f}
    - RSI (14): {tech_summary.get('RSI_14', 'N/A'):.2f}
    - MACD Line: {tech_summary.get('MACD_12_26_9', 'N/A'):.2f}

    **Recent News Summaries:**
    """
    for news in news_summaries:
        prompt_context += f"- ({news['sentiment_label']}) {news['summary']}\n"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI financial analyst. Provide a brief, balanced, and actionable synthesis of the provided technical and news data."
                },
                {
                    "role": "user",
                    "content": prompt_context,
                }
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error getting analyst opinion from Groq: {e}")
        return "AI Analyst opinion could not be generated."

def run_controller(ticker: str, tech_summary: dict, news_summaries: list[dict]) -> dict:
    """Orchestrates the decision-making process."""
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    action, reason = decide_action_with_rules(tech_summary, news_summaries)
    analyst_opinion = get_analyst_opinion(client, ticker, tech_summary, news_summaries)

    print(f"Controller decision for {ticker}: {action} because {reason}")
    return {
        "action": action,
        "reason": reason,
        "analyst_opinion": analyst_opinion
    }
