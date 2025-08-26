import pandas as pd
import mplfinance as mpf
import base64
from io import BytesIO
import matplotlib.pyplot as plt

def generate_chart(df: pd.DataFrame, ticker: str) -> str:
    """Generates a candlestick chart and returns it as a base64 string."""
    # Ensure dataframe is sliced for recent data to make chart readable
    data = df.tail(120) # Last ~6 months approx

    # Plotting
    fig, axlist = mpf.plot(data,
                           type='candle',
                           style='yahoo',
                           title=f'{ticker} Price Chart',
                           ylabel='Price ($)',
                           mav=(20, 50),
                           volume=True,
                           show_nontrading=False,
                           returnfig=True)

    # Save to a bytes buffer
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)

    # Encode in base64
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Close the figure to free memory
    try:
        plt.close(fig)
    except Exception:
        pass

    print(f"Generated chart for {ticker}.")
    return img_base64

def render_html_report(report_data: list[dict]) -> str:
    """Renders the final HTML report from the processed data."""
    ticker_sections_html = ""
    for data in report_data:
        # News Table
        news_html = ""
        if data.get('news'):
            news_html += """"
                <table class="news-table">
                    <tr><th>Headline</th><th>Summary</th><th>Sentiment</th><th>Source</th></tr>
            """
            for article in data['news']:
                sentiment_color = "color: #ff4d4d;" if article.get('sentiment_label') == 'Negative' else "color: #4caf50;" if article.get('sentiment_label') == 'Positive' else ""
                news_html += f""""
                    <tr>
                        <td><a href="{article.get('link','')}">{article.get('headline','')}</a></td>
                        <td>{article.get('summary','')}</td>
                        <td style="{sentiment_color}">{article.get('sentiment_label','')} ({article.get('sentiment_score',0):.2f})</td>
                        <td>{article.get('source','')}</td>
                    </tr>
                """
            news_html += "</table>"
        else:
            news_html = "<p>No recent news found.</p>"

        # Ticker Section
        tech = data.get('tech', {})
        ticker_sections_html += f""""
        <details open>
            <summary>
                <h2>{data.get('ticker','UNKNOWN')} - Daily Report</h2>
            </summary>
            <div class="ticker-section">
                <h3>🤖 AI Analyst Opinion</h3>
                <p class="analyst-opinion">{data.get('controller_output',{}).get('analyst_opinion','')}</p>
                <p><b>Action Triggered:</b> {data.get('controller_output',{}).get('action','')} ({data.get('controller_output',{}).get('reason','')})</p>

                <h3>📈 Technical Summary</h3>
                <p>
                    <b>Close:</b> ${tech.get('Close', 0) if isinstance(tech.get('Close',0), (int,float)) else tech.get('Close', 'N/A')} | 
                    <b>SMA20:</b> ${tech.get('SMA_20', 0) if isinstance(tech.get('SMA_20',0), (int,float)) else tech.get('SMA_20', 'N/A')} | 
                    <b>SMA50:</b> ${tech.get('SMA_50', 0) if isinstance(tech.get('SMA_50',0), (int,float)) else tech.get('SMA_50', 'N/A')} | 
                    <b>RSI:</b> {tech.get('RSI_14', 'N/A')}
                </p>
                <img src="data:image/png;base64,{data.get('chart','')}" alt="{data.get('ticker','')} chart" style="width:100%; max-width:700px;">

                <h3>🗞️ Recent News</h3>
                {news_html}
            </div>
        </details>
        """

    # Final HTML
    html = f""""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
        .container {{ max-width: 800px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        h3 {{ color: #34495e; }}
        details {{ border: 1px solid #ddd; border-radius: 4px; margin-bottom: 15px; }}
        summary {{ font-size: 1.2em; font-weight: bold; padding: 10px; cursor: pointer; background-color: #f2f2f2; }}
        .ticker-section {{ padding: 10px; }}
        .analyst-opinion {{ background-color: #eaf2f8; border-left: 4px solid #3498db; padding: 10px; margin: 10px 0; }}
        .news-table {{ width: 100%; border-collapse: collapse; }}
        .news-table th, .news-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .news-table th {{ background-color: #f2f2f2; }}
    </style>
    </head>
    <body>
    <div class="container">
        <h1>📈 Daily Stock Watcher Report</h1>
        {ticker_sections_html}
    </div>
    </body>
    </html>
    """
    print("Successfully rendered HTML report.")
    return html
