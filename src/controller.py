import os
try:
    from groq import Groq
except Exception:
    Groq = None

def _fmt_num(v):
    try:
        return f"{float(v):.2f}"
    except Exception:
        return "N/A"

def decide_action_with_rules(tech_summary: dict, news_summaries: list[dict]) -> tuple[str, str]:
    """Simple rule-based logic to decide an action."""
    reasons = []

    # Technical Rules
    try:
        if float(tech_summary.get('RSI_14', 50)) >= 70:
            reasons.append("RSI is overbought (>= 70).")
    except Exception:
        pass
    try:
        if float(tech_summary.get('RSI_14', 50)) <= 30:
            reasons.append("RSI is oversold (<= 30).")
    except Exception:
        pass
    try:
        if float(tech_summary.get('Close', 0)) < float(tech_summary.get('SMA_50', float('inf'))):
            reasons.append("Price crossed below 50-day SMA.")
    except Exception:
        pass

    # News Rules
    negative_news_count = sum(1 for article in news_summaries if article.get('sentiment_score', 0) <= -0.2)
    if negative_news_count >= 2:
        reasons.append(f"High volume of negative news ({negative_news_count} articles).")

    if reasons:
        return "ESCALATE", " & ".join(reasons)

    return "MONITOR", "No significant triggers met."


def get_analyst_opinion(client, ticker: str, tech_summary: dict, news_summaries: list[dict]) -> str:
    """Uses Groq to provide a high-level opinion on the current situation."""
    prompt_context = f"""
    Analyze the following data for the stock ticker {ticker} and provide a one-paragraph summary for an investor.
    Should I be concerned, optimistic, or just watchful? Explain why briefly.

    **Technical Data:**
    - Close Price: {_fmt_num(tech_summary.get('Close'))}
    - 20-Day SMA: {_fmt_num(tech_summary.get('SMA_20'))}
    - 50-Day SMA: {_fmt_num(tech_summary.get('SMA_50'))}
    - RSI (14): {_fmt_num(tech_summary.get('RSI_14'))}
    - MACD Line: {_fmt_num(tech_summary.get('MACD_12_26_9'))}

    **Recent News Summaries:**
    """
    if news_summaries:
        for news in news_summaries:
            prompt_context += f"- ({news.get('sentiment_label','')}) {news.get('summary','')}\n"
    else:
        prompt_context += "- No recent news summaries available.\n"

    if client is None:
        # If no Groq client, return a concise non-AI opinion built from rules
        action, reason = decide_action_with_rules(tech_summary, news_summaries)
        return f"{action}: {reason} (No AI analyst available - GROQ_API_KEY missing or groq library not installed.)"

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
        action, reason = decide_action_with_rules(tech_summary, news_summaries)
        return f"{action}: {reason} (AI analyst failed.)"

def run_controller(ticker: str, tech_summary: dict, news_summaries: list[dict]) -> dict:
    """Orchestrates the decision-making process."""
    groq_key = os.environ.get("GROQ_API_KEY")
    client = Groq(api_key=groq_key) if (Groq is not None and groq_key) else None

    action, reason = decide_action_with_rules(tech_summary, news_summaries)
    analyst_opinion = get_analyst_opinion(client, ticker, tech_summary, news_summaries)

    print(f"Controller decision for {ticker}: {action} because {reason}")
    return {
        "action": action,
        "reason": reason,
        "analyst_opinion": analyst_opinion
    }
