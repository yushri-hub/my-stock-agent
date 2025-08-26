import pandas as pd
import numpy as np
import pandas_ta as ta

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Computes technical indicators for the stock data."""
    # Work on a copy to avoid SettingWithCopy warnings
    df = df.copy()

    # Ensure required columns exist
    if 'Close' not in df.columns:
        raise ValueError("Dataframe must contain 'Close' column")

    # Using pandas_ta convenience access
    try:
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=50, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.macd(append=True)
        df.ta.bbands(append=True)
        df.ta.atr(append=True)
        df.ta.obv(append=True)
    except Exception as e:
        print(f"Warning: pandas_ta failed to compute some indicators: {e}")

    # Calculate volatility (30-day rolling standard deviation of log returns)
    try:
        df['log_return'] = ta.log_return(df['Close'])
    except Exception:
        # fallback if ta.log_return not available
        df['log_return'] = np.log(df['Close']).diff()

    df['volatility'] = df['log_return'].rolling(window=30).std() * (252**0.5) # Annualized

    df.dropna(inplace=True)
    print(f"Successfully computed technical indicators. Rows after dropna: {len(df)}")
    return df
