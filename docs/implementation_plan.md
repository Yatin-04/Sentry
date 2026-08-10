# Technical Specification: Multi-Factor Equity Portfolio Construction Engine

**Target Audience:** Senior Software Engineering / PMG Quant Review
**Status:** Segments 1-3 Built. Segments 4-6 Pending.

This document serves as the architectural blueprint and handoff document. It has been heavily upgraded from the initial prototype plan to include production-grade mathematical protections, edge-case handling, and robust ETL logic.

---

## Architecture & System Design

### 1. Data Pipeline (`data_loader.py`)
**Goal:** Ingest and cache daily pricing and fundamental snapshots with minimal API overhead.
*   **Universe:** 98 mega-cap S&P 500 equities (hardcoded to prevent survivorship bias and API timeouts).
*   **Storage:** 
    *   Pricing: `data/cache/price_data.parquet` (fast binary columnar read/write).
    *   Fundamentals: `data/cache/fundamentals.csv` (static snapshot).
*   **ETL Delta Logic:** The pipeline does *not* do full re-downloads. On execution, it reads the parquet file, extracts `max(Date)`, and queries the `yfinance` API strictly for `(max(Date) + 1 day)` to `END_DATE`. 
*   **Date Boundary Protection:** `yfinance` uses exclusive end dates. The API request dynamically adds `+1 day` to the target `END_DATE` to ensure the current day's close is fetched. Overlapping historical rows are explicitly filtered (`index > max_date`) to prevent infinite fetch loops over weekends.

### 2. Factor Engineering (`factor_engine.py` & `factor_utils.py`)
**Goal:** Compute standard academic factors (Value, Quality, Momentum, Low-Vol) and cross-sectionally z-score them.
*   **Winsorization:** All raw cross-sections are clipped at `(0.01, 0.99)` quantiles before z-scoring to prevent singular extreme outliers from skewing the mean/variance.
*   **Mathematical Safety (The Missing Data Rule):** If fundamental data is missing (e.g. no Debt/Equity ratio), the code computes the z-score of the valid data *first*, and then uses `.fillna(0)` on the resulting z-scores. Filling missing data with the raw median *prior* to z-scoring is mathematically invalid.
*   **Value:** Uses Earnings Yield (E/P) and Book Yield (B/P) to gracefully handle zero and negative earnings.
*   **Momentum:** Computes 12-month return skipping the most recent 21 trading days (1 month) to strip out short-term mean reversion noise.
*   **Target Variable (`compute_forward_returns`):** Target `Y` is computed strictly using `.shift(-21)` along the trading-day index. This aligns features at $T$ with returns from $T$ to $T+21$, mathematically preventing look-ahead bias.

### 3. Portfolio Optimizer (`optimizer.py`)
**Goal:** Translate alpha scores into tradable weights using convex optimization (`cvxpy`).
*   **Objective:** $\max_w \; \alpha^T w - \frac{\lambda}{2} w^T \Sigma w$
*   **Covariance Estimation:** Ledoit-Wolf shrinkage is applied to trailing 252-day returns to stabilize the covariance matrix inversion.
*   **PSD Projection:** `cvxpy` will crash if the covariance matrix is not strictly Positive Semi-Definite (PSD). Floating point arithmetic often yields eigenvalues of `-1e-16`. The `make_closest_psd()` function intercepts the matrix, runs eigenvalue decomposition, clips negative roots to `1e-8`, and rebuilds the matrix.
*   **Execution Safety (Micro-trades):** Optimal weights $< 0.0001$ (1 bps) are hard-forced to `0.0`. The remaining weights are re-normalized to strictly sum to `1.0`.
*   **The 4-Tier Infeasibility Fallback Cascade:**
    *   **Tier 1:** Solve with all constraints (Sum=1, Long-only, Max 5% position, Max 40% turnover, Sector neutrality ±5%).
    *   **Tier 2:** If mathematically infeasible, relax Turnover constraint.
    *   **Tier 3:** If still infeasible, relax Sector Neutrality bounds.
    *   **Tier 4:** If all SOCP/QP solvers fail (e.g. DCP errors, strict solver divergence), bypass `cvxpy` and execute `heuristic_fallback_weights()`, which simply allocates the maximum position size to the top-ranked alpha scores. **The pipeline is guaranteed to never return a null portfolio.**

---

## Remaining Work (Segments 4-6)

### Segment 4 — XGBoost Alpha Model (`alpha_model.py`)
*   **Objective:** Predict the cross-sectional rank of 1-month forward returns using the 4 factor z-scores.
*   **Training Loop:** Walk-forward expanding window. At rebalance date $T$, train on all data from $T_0$ to $T-1$. Predict on features at $T$. 
*   **Architecture:** `XGBRegressor(objective='rank:ndcg')` or standard MSE if rank is unstable.
*   **Fallback (`alpha_fallback.py`):** Equal-weighted z-score composite $\alpha_i = \frac{1}{4}\sum_{f} z_{i,f}$. Used if ML tuning is blocked.

### Segment 5 — Backtest Engine (`backtester.py` & `metrics.py`)
*   **Loop:** Monthly rebalance. Compute factors $\rightarrow$ Generate Alpha $\rightarrow$ Optimize Weights $\rightarrow$ Apply Weights $\rightarrow$ Hold for 21 days (drift un-rebalanced).
*   **Benchmark:** Equal-weight universe.
*   **Metrics:** Annualized Return, Volatility, Sharpe Ratio, Max Drawdown, Information Ratio, Average Turnover.

### Segment 6 — Streamlit Dashboard (`app.py`)
*   **Visuals (Plotly):** Cumulative returns, rolling drawdown, dynamic holdings table, factor exposure stacked area chart.
*   **Rationale:** Proves capability to build stakeholder-facing interactive analytics (ports directly to PowerBI/Tableau logic).

---

## Known Flaws (Proactive Disclosures for Review)
1. **Point-in-Time Fundamentals:** `yfinance` provides a static snapshot. True backtesting requires WRDS/Compustat PIT data to avoid look-ahead bias in fundamental factors.
2. **Transaction Costs:** Modeled strictly as a turnover constraint limit. A true implementation requires a non-linear slippage/impact penalty in the objective function.
3. **Risk Model:** Ledoit-Wolf historical shrinkage is robust, but a fundamental factor risk model (e.g. Barra) provides vastly superior future covariance forecasts.
