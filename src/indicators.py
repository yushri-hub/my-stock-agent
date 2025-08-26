import pandas as pd
import pandas_ta as ta

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Computes technical indicators for the stock data."""
    df.ta.sma(length=20, append=True)
    df.ta.sma(length=50, append=True)
    df.ta.rsi(length=14, append=True)
    df.ta.macd(append=True)
    df.ta.bbands(append=True)
    df.ta.atr(append=True)
    df.ta.obv(append=True)

    # Calculate volatility (30-day rolling standard deviation of returns)
    df['log_return'] = ta.log_return(df['Close'])
    df['volatility'] = df['log_return'].rolling(window=30).std() * (252**0.5) # Annualized

    df.dropna(inplace=True)
    print(f"Successfully computed technical indicators.")
    return df
