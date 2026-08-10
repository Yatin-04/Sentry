import yfinance as yf
import pandas as pd
import os
import json
from config import UNIVERSE, START_DATE, END_DATE, CACHE_DIR

PRICE_CACHE_FILE = os.path.join(CACHE_DIR, 'price_data.parquet')
FUNDAMENTALS_CACHE_FILE = os.path.join(CACHE_DIR, 'fundamentals.csv')

def fetch_price_data(force_reload=False):
    """
    Downloads daily OHLCV data for the universe.
    Implements a production-style delta update: if cache exists, it only 
    downloads the missing days since the last run and appends to the cache.
    """
    if force_reload and os.path.exists(PRICE_CACHE_FILE):
        os.remove(PRICE_CACHE_FILE)

    # yfinance 'end' parameter is EXCLUSIVE. To get data for END_DATE, we must ask for END_DATE + 1 day
    yf_end_date = (pd.to_datetime(END_DATE) + pd.Timedelta(days=1)).strftime('%Y-%m-%d')

    if os.path.exists(PRICE_CACHE_FILE):
        print(f"Loading price data from cache: {PRICE_CACHE_FILE}")
        cached_data = pd.read_parquet(PRICE_CACHE_FILE)
        
        # Get the latest date in the cache (index is Date)
        max_date = cached_data.index.max()
        end_date_pd = pd.to_datetime(END_DATE)
        
        # If the cache is behind our target END_DATE, fetch the delta
        if max_date < end_date_pd:
            new_start = (max_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            print(f"Cache is stale (last date: {max_date.strftime('%Y-%m-%d')}). Fetching delta from {new_start} to {END_DATE}...")
            
            delta_data = yf.download(
                tickers=UNIVERSE, 
                start=new_start, 
                end=yf_end_date, 
                group_by='ticker',
                auto_adjust=False,
                threads=True
            )
            
            # yfinance sometimes returns the last trading day BEFORE the start date
            # We must explicitly filter out dates we already have
            delta_data = delta_data[delta_data.index > max_date]
            
            if not delta_data.empty and len(delta_data) > 0:
                # Append, drop any accidental overlapping dates, and save
                combined_data = pd.concat([cached_data, delta_data])
                combined_data = combined_data[~combined_data.index.duplicated(keep='last')]
                combined_data.to_parquet(PRICE_CACHE_FILE)
                print("Delta appended and cache updated.")
                return combined_data
            else:
                print("No new trading days found. Using existing cache.")
                return cached_data
        else:
            print("Cache is up to date.")
            return cached_data

    # If no cache exists, do a full download
    print(f"No cache found. Downloading full history for {len(UNIVERSE)} tickers...")
    data = yf.download(
        tickers=UNIVERSE, 
        start=START_DATE, 
        end=yf_end_date, 
        group_by='ticker',
        auto_adjust=False, 
        threads=True
    )
    
    data.to_parquet(PRICE_CACHE_FILE)
    print("Full price data cached successfully.")
    return data

def fetch_fundamentals_and_sectors(force_reload=False):
    """
    Fetches point-in-time snapshot of fundamentals and sector mappings.
    WARNING: yfinance only provides *current* fundamentals. 
    Using this for historical backtesting introduces look-ahead bias.
    """
    if not force_reload and os.path.exists(FUNDAMENTALS_CACHE_FILE):
        print(f"Loading fundamentals from cache: {FUNDAMENTALS_CACHE_FILE}")
        return pd.read_csv(FUNDAMENTALS_CACHE_FILE, index_col='Ticker')

    print(f"Fetching fundamentals for {len(UNIVERSE)} tickers...")
    records = []
    
    for ticker in UNIVERSE:
        try:
            info = yf.Ticker(ticker).info
            records.append({
                'Ticker': ticker,
                'Sector': info.get('sector', 'Unknown'),
                'Industry': info.get('industry', 'Unknown'),
                'ForwardPE': info.get('forwardPE', None),
                'TrailingPE': info.get('trailingPE', None),
                'PriceToBook': info.get('priceToBook', None),
                'ROE': info.get('returnOnEquity', None),
                'DebtToEquity': info.get('debtToEquity', None),
                'MarketCap': info.get('marketCap', None)
            })
        except Exception as e:
            print(f"Failed to fetch data for {ticker}: {e}")
            
    df = pd.DataFrame(records)
    df.set_index('Ticker', inplace=True)
    df.to_csv(FUNDAMENTALS_CACHE_FILE)
    print("Fundamentals cached successfully.")
    
    return df

if __name__ == "__main__":
    # Test the pipeline
    prices = fetch_price_data()
    print(f"Prices shape: {prices.shape}")
    
    funds = fetch_fundamentals_and_sectors()
    print(f"Fundamentals shape: {funds.shape}")
    print(funds.head())
