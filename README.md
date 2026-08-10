<div align="center">
  <h1 align="center">Sentry: Quantitative Alpha Engine</h1>
  <p align="center">
    An institutional-grade, multi-factor algorithmic trading simulation powered by Machine Learning and Convex Optimization.
  </p>
</div>

<br />

## 📖 Overview

**Sentry** is an end-to-end quantitative trading simulation pipeline designed to bridge traditional multi-factor equity investing with modern machine learning. 

Instead of relying on single historical factors, Sentry ingests raw market data, computes fundamental Z-scores (Value, Quality, Momentum, Low-Volatility), and trains an **XGBoost** model using a strict walk-forward expanding window to predict relative stock outperformance. Those predictions act as Alpha signals fed into a mathematical **Convex Optimizer**, maximizing return while strictly controlling for portfolio turnover, position sizing, and sector neutrality.

The final output is simulated against realistic market frictions (transaction costs and portfolio drift) and visualized in a premium, Bloomberg-style **Streamlit Dashboard**.

---

## 🏗️ Architecture & Pipeline

The system is modularized into 6 core segments:

1. **Data Ingestion (`data_loader.py`)**: Fetches daily price and fundamental data for a universe of ~100 mega-cap US equities via Yahoo Finance, utilizing a smart delta-append cache to minimize API overhead.
2. **Factor Engineering (`factor_engine.py`)**: Normalizes raw data into cross-sectional Z-scores for 4 canonical factors: Value (E/P, B/P), Quality (ROE, Debt/Equity), Momentum (12-1 Month), and Low-Volatility (Trailing 60-Day).
3. **Alpha Generation (`alpha_model.py`)**: A Time-Series Machine Learning Engine (XGBoost) that trains on a strictly expanding historical window to avoid look-ahead bias, predicting the future cross-sectional rank of stock returns.
4. **Risk & Convex Optimization (`optimizer.py`)**: Constructs a Ledoit-Wolf shrunk covariance matrix and uses `CVXPY` to solve a constrained convex optimization problem (maximizing Alpha minus Risk Penalty, subject to turnover, weight, and sector bounds).
5. **Backtest Simulation (`backtester.py`)**: A time-machine loop that walks through history month-by-month. It handles real-world frictions by applying a 10 bps transaction cost penalty on two-way turnover and precisely calculating daily portfolio weight drift.
6. **Executive Dashboard (`app.py`)**: A high-performance, asynchronous Streamlit UI featuring glassmorphism CSS and Plotly charts. It loads serialized simulation results to display the Equity Curve, Historical Drawdown, and Live Portfolio Holdings instantly.

---

## 🚀 Getting Started

### Prerequisites

Ensure you have Python 3.9+ installed. Install the required quantitative libraries:

```bash
pip install pandas numpy yfinance xgboost cvxpy scikit-learn streamlit plotly
```

### 1. Run the Backtest Engine

To start the simulation, execute the backtester. 
*Note: The first run will perform a full historical data download (from 2018 to present) which may take 1-2 minutes. Subsequent runs will use the local parquet cache and execute in ~15 seconds.*

```bash
python backtester.py
```

**What this does:**
- Updates the local data cache.
- Runs the 6-year monthly Walk-Forward ML loop.
- Optimizes the portfolio and calculates drifted returns.
- Serializes the final state to `data/output/backtest_results.pkl`.

### 2. Launch the Premium Dashboard

Once the backtester finishes, launch the executive UI to visualize the performance tear-sheet:

```bash
streamlit run app.py
```

This will automatically open the interactive dashboard in your default web browser.

---

## 🔬 Key Engineering Features

- **Strict Look-Ahead Bias Prevention**: The ML model exclusively uses an expanding window (`X_train.index < rebalance_date`), guaranteeing zero leakage of future data into past training sets.
- **Robust Mathematical Fail-safes**: The covariance estimator projects matrices to the nearest Positive Semi-Definite (PSD) state to prevent `cvxpy` crashes during highly volatile market regimes.
- **Multi-Tier Optimizer Fallback**: If strict turnover constraints render the optimization infeasible, the system systematically relaxes turnover, then sector bounds, and finally defaults to a heuristic allocation to guarantee continuous execution.
- **Realistic Friction Modeling**: Incorporates exact daily portfolio weight drift calculations and explicit transaction cost deductions (10 bps), avoiding the "fantasy returns" common in academic backtests.

---

## ⚠️ Disclaimer
*This repository is for educational and portfolio demonstration purposes only. The models and strategies contained herein do not constitute financial advice. Algorithmic trading involves significant risk of loss.*
