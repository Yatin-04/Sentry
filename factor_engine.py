import pandas as pd
import numpy as np
from factor_utils import cross_sectional_zscore

def compute_value_factor(fundamentals_df):
    """
    Computes a composite Value factor from P/E and P/B.
    We use Earnings Yield (E/P) and Book Yield (B/P) because ratios with 
    prices in the denominator handle zero/negative earnings much better mathematically.
    """
    # Inverse P/E is E/P (Earnings Yield)
    # If ForwardPE is missing, fallback to TrailingPE
    pe_ratio = fundamentals_df['ForwardPE'].fillna(fundamentals_df['TrailingPE'])
    ep_yield = 1.0 / pe_ratio.replace(0, np.nan) # avoid division by zero
    
    # Inverse P/B is B/P (Book Yield)
    bp_yield = 1.0 / fundamentals_df['PriceToBook'].replace(0, np.nan)
    
    # Cross-sectional z-score each component, handle missing values by assigning the mean (0)
    ep_z = cross_sectional_zscore(ep_yield).fillna(0)
    bp_z = cross_sectional_zscore(bp_yield).fillna(0)
    
    # Combine and z-score the composite
    value_composite = ep_z + bp_z
    return cross_sectional_zscore(value_composite).fillna(0)

def compute_quality_factor(fundamentals_df):
    """
    Computes a composite Quality factor: High ROE, Low Debt/Equity.
    """
    roe = fundamentals_df['ROE']
    de_ratio = fundamentals_df['DebtToEquity']
    
    # Fill missing z-scores with 0 (market average)
    roe_z = cross_sectional_zscore(roe).fillna(0)
    # We want LOW debt, so we negate the Debt/Equity z-score
    de_z = -cross_sectional_zscore(de_ratio).fillna(0)
    
    quality_composite = roe_z + de_z
    return cross_sectional_zscore(quality_composite).fillna(0)

def compute_momentum_factor(prices_df, date):
    """
    Computes 12-1 month momentum.
    Return from 252 trading days ago to 21 trading days ago.
    Skipping the most recent month avoids the short-term reversal effect.
    """
    # Get index of the target date
    try:
        date_idx = prices_df.index.get_loc(date)
    except KeyError:
        # If exact date isn't a trading day, find previous trading day
        past_dates = prices_df.index[prices_df.index <= date]
        if len(past_dates) == 0:
            return pd.Series(index=prices_df.columns, dtype=float)
        date_idx = prices_df.index.get_loc(past_dates[-1])

    # Need at least 252 days of history
    if date_idx < 252:
        return pd.Series(index=prices_df.columns, dtype=float)

    # Price 12 months ago
    price_12m_ago = prices_df.iloc[date_idx - 252]
    # Price 1 month ago
    price_1m_ago = prices_df.iloc[date_idx - 21]
    
    # 11-month return skipping the most recent month
    mom_returns = (price_1m_ago - price_12m_ago) / price_12m_ago
    
    return cross_sectional_zscore(mom_returns).fillna(0) # 0 is the cross-sectional mean

def compute_low_vol_factor(prices_df, date):
    """
    Computes trailing 60-day realized volatility.
    Lower volatility = higher score (negated z-score).
    """
    try:
        date_idx = prices_df.index.get_loc(date)
    except KeyError:
        past_dates = prices_df.index[prices_df.index <= date]
        if len(past_dates) == 0:
            return pd.Series(index=prices_df.columns, dtype=float)
        date_idx = prices_df.index.get_loc(past_dates[-1])

    if date_idx < 60:
        return pd.Series(index=prices_df.columns, dtype=float)

    # 60 day slice
    price_slice = prices_df.iloc[date_idx - 60 : date_idx + 1]
    daily_returns = price_slice.pct_change().dropna(how='all')
    
    # Annualized volatility
    vol = daily_returns.std() * np.sqrt(252)
    
    # We want LOW volatility, so we negate it before z-scoring
    return cross_sectional_zscore(-vol).fillna(0)

def generate_alpha_factors(prices_df, fundamentals_df, rebalance_dates):
    """
    Iterates through rebalance dates and computes the 4 factors for each point in time.
    Returns a MultiIndex DataFrame (Date, Ticker) -> Factor Scores
    """
    print("Computing factor scores over time...")
    
    # We can pre-compute Value and Quality since our fundamental dataset is a static snapshot
    # (Reminder: this is the look-ahead bias flaw we documented)
    static_value = compute_value_factor(fundamentals_df)
    static_quality = compute_quality_factor(fundamentals_df)
    
    records = []
    
    for date in rebalance_dates:
        # These change every month based on price history
        mom_z = compute_momentum_factor(prices_df, date)
        vol_z = compute_low_vol_factor(prices_df, date)
        
        for ticker in prices_df.columns:
            # Skip if we don't have valid price data for momentum/volatility
            if pd.isna(mom_z[ticker]) or pd.isna(vol_z[ticker]):
                continue
                
            records.append({
                'Date': date,
                'Ticker': ticker,
                'Value': static_value.get(ticker, 0),
                'Quality': static_quality.get(ticker, 0),
                'Momentum': mom_z[ticker],
                'LowVol': vol_z[ticker]
            })
            
    df = pd.DataFrame(records)
    if not df.empty:
        df.set_index(['Date', 'Ticker'], inplace=True)
    return df
