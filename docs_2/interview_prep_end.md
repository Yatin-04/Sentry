# Interview Prep: Project Conclusion & Holistic View (End)

This document provides a 10,000-foot view of the Sentry project. Use this for the "Tell me about a project you've built" open-ended behavioral questions.

## 1. The Elevator Pitch

> [!TIP]
> **Interview Question:** *Walk me through your Sentry AI Alpha Engine project. What was the goal and what did you build?*
> 
> **Your Answer:** 
> "Sentry is an end-to-end quantitative trading simulation pipeline. The goal was to bridge traditional multi-factor investing with modern machine learning. 
> I built a 6-phase pipeline: It automatically ingests data for 100 mega-cap equities, normalizes fundamental and price data into Value, Quality, Momentum, and Low-Volatility Z-scores. It then uses an Expanding-Window XGBoost model to predict relative stock outperformance. Those predictions act as Alpha scores fed into a convex optimizer (CVXPY) which maximizes return while strictly capping turnover, position size, and sector drift. Finally, it runs through a realistic backtest engine accounting for transaction costs and portfolio drift, outputting to an institutional-grade Streamlit dashboard."

## 2. The Biggest Challenge

> [!WARNING]
> **Interview Question:** *What was the hardest technical challenge you faced while building this?*
> 
> **Your Answer:** 
> "The hardest challenge was ensuring the Convex Optimizer didn't crash the entire simulation during highly volatile market regimes. 
> In quantitative finance, covariance matrices must be Positive Semi-Definite (PSD). Even with Ledoit-Wolf shrinkage, floating-point math anomalies would occasionally create tiny negative eigenvalues (-1e-16), causing CVXPY to throw a DCPError.
> I had to build a robust mathematical bridge: explicitly projecting the matrix to the nearest PSD matrix using eigenvalue decomposition. Additionally, I built a multi-tier fallback system inside the optimizer. If it couldn't find a solution with strict turnover bounds, it would relax turnover, then relax sector bounds, and if all convex optimization failed, it would trigger a heuristic fallback. This guaranteed the pipeline would never crash mid-simulation."

## 3. What You Would Do Differently

> [!CAUTION]
> **Interview Question:** *If you had 3 more months to work on this, what would you change or improve?*
> 
> **Your Answer:** 
> "Three things:
> 1. **Eliminate Look-Ahead Bias**: I would integrate a proper point-in-time fundamental database (like Compustat or Sharadar) instead of using Yahoo Finance's static snapshot.
> 2. **Alternative Data**: I would add natural language processing (FinBERT) sentiment scores from SEC 10-K filings or earnings call transcripts as an additional factor.
> 3. **Hyperparameter Tuning**: Currently, the XGBoost hyperparameters (depth=3, lr=0.05) are static. I would implement an automated time-series grid search (like `TimeSeriesSplit`) to dynamically adjust the parameters as market regimes shift."
