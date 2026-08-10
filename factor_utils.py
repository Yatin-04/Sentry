import pandas as pd
import numpy as np

def winsorize_series(series, limits=(0.01, 0.99)):
    """
    Clips extreme values in a pandas Series to the given quantiles.
    This prevents a single extreme stock from blowing up the z-score mean/std.
    """
    lower_bound = series.quantile(limits[0])
    upper_bound = series.quantile(limits[1])
    return series.clip(lower=lower_bound, upper=upper_bound)

def cross_sectional_zscore(series):
    """
    Winsorizes then normalizes a cross-section of data.
    Result has mean ~0 and std ~1.
    """
    winsorized = winsorize_series(series)
    return (winsorized - winsorized.mean()) / winsorized.std()

def compute_forward_returns(prices_df, rebalance_dates, holding_period_days=21):
    """
    Computes the target variable: what the return of the stock will be over the next month.
    Critically, this looks FORWARD from the rebalance date.
    Prices is expected to be a DataFrame where columns are Tickers and index is Date.
    """
    # 21 trading days is approx 1 month
    # We calculate the return from T to T+21
    # .shift(-holding_period_days) brings future prices back to today's row
    future_prices = prices_df.shift(-holding_period_days)
    forward_returns = (future_prices - prices_df) / prices_df
    
    # We only care about forward returns on the specific dates we rebalance
    valid_dates = [d for d in rebalance_dates if d in forward_returns.index]
    return forward_returns.loc[valid_dates]
