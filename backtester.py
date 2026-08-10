import pandas as pd
import numpy as np
from datetime import timedelta
import os

from data_loader import fetch_price_data, fetch_fundamentals_and_sectors
from factor_utils import compute_forward_returns
from factor_engine import generate_alpha_factors
from alpha_model import generate_ml_alpha
from optimizer import estimate_covariance, get_sector_matrices, optimize_portfolio
from metrics import generate_performance_report

def run_backtest():
    print("Initializing Sentry Backtest Engine...")
    
    # 1. Load Data
    prices_df = fetch_price_data(force_reload=False)
    # Use Adjusted Close for accurate historical returns calculation
    adj_prices = prices_df['Adj Close'].copy()
    
    fundamentals_df = fetch_fundamentals_and_sectors(force_reload=False)
    
    # 2. Determine Rebalance Dates (End of Month)
    # Resample to monthly and get the last trading day of each month
    monthly_dates = adj_prices.resample('ME').last().index
    
    # Filter to dates where we actually have data, starting from 2018
    monthly_dates = [d for d in monthly_dates if d >= pd.to_datetime('2018-01-01')]
    
    print(f"Total rebalance periods found: {len(monthly_dates)}")
    
    # 3. Pre-compute Target Returns and Factors (for the ML training loop)
    # We pre-compute this outside the loop to save massive amounts of time
    print("Pre-computing historical factor scores and forward returns...")
    # Shift -21 for 1-month forward return
    forward_returns = compute_forward_returns(adj_prices, monthly_dates, holding_period_days=21) 
    factor_scores = generate_alpha_factors(adj_prices, fundamentals_df, monthly_dates)
    
    if factor_scores.empty:
        print("ERROR: Failed to generate factor scores.")
        return
        
    # Set up Sector Matrices (Static for the backtest)
    tickers = adj_prices.columns
    sector_matrix, benchmark_sector_weights = get_sector_matrices(fundamentals_df, tickers)
    
    # 4. State Tracking Variables
    portfolio_daily_values = pd.Series(dtype=float)
    current_weights = pd.Series(0.0, index=tickers)
    
    # Start the portfolio at 1.0 (or $1)
    current_portfolio_value = 1.0 
    
    TRANSACTION_COST_BPS = 0.0010 # 10 basis points per dollar traded (0.10%)
    
    print("Starting Historical Walk-Forward Simulation...")
    
    # Loop through history
    for i in range(len(monthly_dates) - 1):
        rebalance_date = monthly_dates[i]
        next_rebalance_date = monthly_dates[i+1]
        
        print(f"\n--- Rebalancing for {rebalance_date.strftime('%Y-%m-%d')} ---")
        
        # --- PHASE 1: Generate Alpha (ML Walk-Forward) ---
        alpha_scores = generate_ml_alpha(factor_scores, forward_returns, rebalance_date)
        
        if alpha_scores is None or alpha_scores.empty:
            print("Skipping rebalance due to lack of ML predictions (burn-in period).")
            continue
            
        # --- PHASE 2: Covariance Estimation ---
        # Get trailing 1 year (252 days) of returns for covariance
        try:
            date_idx = adj_prices.index.get_loc(rebalance_date)
        except KeyError:
            continue
            
        if date_idx < 252:
            print("Not enough history for covariance estimation.")
            continue
            
        returns_slice = adj_prices.iloc[date_idx-252:date_idx].pct_change().dropna(how='all')
        cov_matrix = estimate_covariance(returns_slice)
        
        # --- PHASE 3: Convex Optimization ---
        # Align alpha scores with the covariance matrix index
        aligned_alpha = alpha_scores.reindex(tickers).fillna(0)
        
        target_weights = optimize_portfolio(
            aligned_alpha, 
            cov_matrix, 
            current_weights, 
            sector_matrix, 
            benchmark_sector_weights
        )
        
        # Calculate Turnover and apply Transaction Costs
        weight_diff = np.abs(target_weights - current_weights).sum()
        transaction_cost = weight_diff * TRANSACTION_COST_BPS
        
        # The portfolio value drops slightly due to trading fees
        current_portfolio_value *= (1 - transaction_cost)
        print(f"Turnover: {weight_diff*100:.2f}% | TC Penalty: -{transaction_cost*100:.3f}%")
        
        # --- PHASE 4: Simulate Holding Period Drift ---
        # Extract daily prices for the holding period
        holding_prices = adj_prices.loc[(adj_prices.index >= rebalance_date) & (adj_prices.index <= next_rebalance_date)]
        
        if holding_prices.empty or len(holding_prices) < 2:
            continue
            
        # Calculate daily cumulative return of the stocks over this specific month
        # Normalize prices to 1.0 at the start of the month
        price_relatives = holding_prices / holding_prices.iloc[0]
        
        # Daily portfolio value = Target Weights dot-product with Daily Price Relatives
        daily_portfolio_returns = price_relatives.dot(target_weights)
        
        # Scale to actual portfolio cash value
        daily_cash_values = daily_portfolio_returns * current_portfolio_value
        
        # Append to our master tracker
        portfolio_daily_values = pd.concat([portfolio_daily_values, daily_cash_values.iloc[1:]])
        
        # Update current state for the next loop
        current_portfolio_value = daily_cash_values.iloc[-1]
        
        # Calculate drifted weights at the end of the month
        # Weight = (Initial Weight * Price Relative) / Total Portfolio Return
        end_price_relatives = price_relatives.iloc[-1]
        current_weights = (target_weights * end_price_relatives) / daily_portfolio_returns.iloc[-1]
        
    # --- PHASE 5: Benchmark & Metrics ---
    print("\nSimulation Complete. Calculating Performance Metrics...")
    
    # Calculate daily percentage returns from the wealth index
    strategy_returns = portfolio_daily_values.pct_change().dropna()
    
    # Create Equal-Weight Benchmark
    # Just take the mean of all stock returns each day
    all_returns = adj_prices.pct_change().dropna(how='all')
    benchmark_returns = all_returns.mean(axis=1)
    
    # Align benchmark dates to our strategy's active trading dates
    benchmark_returns = benchmark_returns.loc[strategy_returns.index]
    
    report = generate_performance_report(strategy_returns, benchmark_returns)
    
    print("\n=========================================")
    print("       SENTRY BACKTEST TEAR-SHEET        ")
    print("=========================================")
    print(report.round(4))
    print("=========================================\n")

if __name__ == "__main__":
    run_backtest()
