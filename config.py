import pandas as pd
import os
from datetime import datetime

# Base directory for caching and outputs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CACHE_DIR = os.path.join(DATA_DIR, 'cache')

# Ensure directories exist
os.makedirs(CACHE_DIR, exist_ok=True)

# Date Range (Using up to today's data for maximum recent-regime visibility)
START_DATE = '2018-01-01'
END_DATE = datetime.today().strftime('%Y-%m-%d')

# Universe: ~100 Liquid Large-Cap US Equities
# We cap this around 100 to avoid massive API rate limits from Yahoo Finance 
# and to keep the covariance matrix inversion fast during optimization prototyping.
UNIVERSE = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'BRK-B', 'TSLA', 'LLY', 'V', 
    'JPM', 'UNH', 'WMT', 'JNJ', 'XOM', 'PG', 'MA', 'ORCL', 'HD', 'CVX', 
    'MRK', 'ABBV', 'COST', 'PEP', 'BAC', 'KO', 'AVGO', 'TMO', 'CSCO', 'MCD', 
    'ACN', 'CRM', 'ADBE', 'ABT', 'LIN', 'NFLX', 'DHR', 'AMD', 'TXN', 'NKE', 
    'PM', 'WFC', 'DIS', 'INTC', 'COP', 'NEE', 'PFE', 'CAT', 'VZ', 'IBM', 
    'UNP', 'INTU', 'GE', 'AMAT', 'NOW', 'HON', 'BA', 'QCOM', 'SPGI', 'AMGN', 
    'RTX', 'LOW', 'SYK', 'GS', 'PLD', 'ELV', 'BKNG', 'BLK', 'MDT', 'TJX', 
    'AXP', 'ISRG', 'SYY', 'CB', 'LMT', 'GILD', 'REGN', 'ZTS', 'MO',
    'DE', 'ADI', 'C', 'AMT', 'PGR', 'SCHW', 'SO', 'BSX', 'PANW', 'CI', 
    'ADP', 'GPN', 'VRTX', 'MU', 'KLAC', 'LRCX', 'SNPS'
]

# Constraint Parameters
MAX_POSITION_SIZE = 0.05       # 5% max weight per stock
SECTOR_DEVIATION_CAP = 0.05    # ±5% sector weight vs benchmark
MAX_TURNOVER = 0.40            # 40% two-way turnover per rebalance
RISK_AVERSION = 1.0            # Penalty on variance in objective function
