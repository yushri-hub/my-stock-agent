import os
from datetime import datetime
from dotenv import load_dotenv

from fetchers import fetch_history, fetch_news
from indicators import compute_indicators
from summarizer import process_articles
from controller import run_controller
from utils import generate_chart, render_html_report
from mailer import send_email

# --- Configuration ---
# For local testing, create a .env file with your secrets
# EMAIL_USER=your_email@gmail.com
# EMAIL_PASS=your_app_password
# GROQ_API_KEY=your_groq_api_key
# RECIPIENT_EMAIL=email_to_send_report_to@example.com
load_dotenv() 

TICKERS = ['AMD', 'AVGO']
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")

def run():
    """Main function to run the stock agent."""
    print("🚀 Starting the stock watcher agent...")
    all_ticker_data = []

    for ticker in TICKERS:
        print(f"\nProcessing ticker: {ticker}...")
        try:
            # 1. Fetch data
            hist_df = fetch_history(ticker)
            articles = fetch_news(ticker)

            # 2. Compute & Analyze
            hist_with_indicators = compute_indicators(hist_df)
            tech_summary = hist_with_indicators.iloc[-1].to_dict()
            processed_news = process_articles(articles)

            # 3. Agentic Controller
            controller_output = run_controller(ticker, tech_summary, processed_news)

            # 4. Generate Visuals
            chart_base64 = generate_chart(hist_with_indicators, ticker)

            all_ticker_data.append({
                'ticker': ticker,
                'tech': tech_summary,
                'news': processed_news,
                'chart': chart_base64,
                'controller_output': controller_output
            })

        except Exception as e:
            print(f"❌ Failed to process {ticker}: {e}")
            # Optionally, you can add this error to the report
            all_ticker_data.append({'ticker': ticker, 'error': str(e)})

    # 5. Render and Send Report
    if all_ticker_data:
        report_html = render_html_report(all_ticker_data)

        # Save report to a file (useful for GitHub Actions artifact)
        os.makedirs("report", exist_ok=True)
        report_path = "report/stock_report.html"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_html)
        print(f"HTML report saved to {report_path}")

        # Send the email
        today_date = datetime.now().strftime('%Y-%m-%d')
        send_email(
            subject=f"Stock Watcher Daily Report - {today_date}",
            html_content=report_html,
            to_email=RECIPIENT_EMAIL
        )

    print("\n✅ Stock watcher agent finished.")

if __name__ == '__main__':
    run()
