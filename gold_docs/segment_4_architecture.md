# Segment 4: Architecture & Working (Machine Learning Alpha Model)

This document explains the core workflow and the crucial design decisions made when transitioning from a simple average factor score to a Machine Learning-driven Alpha signal.

## 1. How Segment 4 Works (The Data Flow)

1. **Feature Ingestion ($X$):** The system receives the cross-sectional z-scores of the 4 factors (Value, Quality, Momentum, LowVol) from Segment 2. 
2. **Target Transformation ($Y$):** The raw 1-month forward returns are converted into a cross-sectional percentile rank (0.0 to 1.0). We do not predict absolute returns (MSE); we predict ranking.
3. **Walk-Forward Training Loop:** As the backtester moves through time, it stops at each month, gathers all historical data *prior* to that month, and trains a brand new XGBoost model on the spot. 
4. **Prediction:** The freshly trained model evaluates today's factor scores and outputs the predicted ranking of stocks for the next month. These predictions become the Alpha scores fed into the Optimizer (Segment 3).

## 2. Key Implementation Decisions (The "Why")

### A. Why XGBoost instead of Deep Learning (LSTMs / NNs)?
Financial data is extremely noisy (low signal-to-noise ratio) and highly tabular. Deep learning models easily overfit to noise in tabular data unless regularized heavily. Tree-based ensemble models like XGBoost handle non-linear relationships well, are robust to outliers, and crucially, are computationally fast enough to be retrained repeatedly during a backtest.

### B. The Fallback Mechanism (Tier-4 Safety Net)
**Decision:** If the XGBoost model crashes, fails to converge, or has insufficient data (e.g., in the first 2 years of the backtest), the system automatically defaults to an equal-weighted composite z-score. 
**Rationale:** In a production pipeline, an ML failure should not result in an empty portfolio and stop trading operations. The system must gracefully degrade to a simpler, proven mathematical heuristic.

### C. Hyperparameter Choices (Shallow Trees)
**Decision:** We strictly enforce `ML_XGB_MAX_DEPTH = 3`. 
**Rationale:** Deep decision trees (e.g., depth 10) will memorize specific historical market anomalies and crashes (overfitting). Shallow trees force the model to only learn broad, generalizable patterns between factors and returns, which holds up better out-of-sample.

---

## 3. The Grand Workflow (How All Segments Connect)

To understand how the entire engine operates end-to-end, it is crucial to note that **Segment 4 runs BEFORE Segment 3** in the live data flow. Here is the step-by-step pipeline:

#### 🚚 1. Segment 1: The Supplier (Data Pipeline)
*   **Role:** Raw Material Ingestion.
*   Pulls daily closing prices and fundamental data (P/E Ratio, Debt, etc.) for the 98 mega-cap companies from Yahoo Finance. It caches this locally to minimize API hits.

#### ⚙️ 2. Segment 2: The Engineer (Factor Engine)
*   **Role:** Standardization & Processing.
*   Raw prices and debt ratios cannot be compared mathematically. Segment 2 applies cross-sectional Z-Scoring and Winsorization. It grades every stock across 4 standard subjects: **Value, Quality, Momentum, Low-Vol**.

#### 🧠 3. Segment 4: The Brain (Machine Learning AI)
*   **Role:** Pattern Recognition & Prediction.
*   Segment 2 provides the grades, but which subject matters most today? Segment 4 (XGBoost) looks at these grades, studies historical patterns, and predicts the **Alpha Scores (Future Ranks)** based on current market regimes (e.g., "In this environment, Apple should be Rank 1, Tesla Rank 98").

#### 🛡️ 4. Segment 3: The Risk Manager (Convex Optimizer)
*   **Role:** Translation to a Safe Portfolio.
*   The AI is smart but blind to risk. Segment 4 hands its predicted ranks to Segment 3.
*   Segment 3 acts as the strict manager: *"I see you want to put all our money into Apple and Exxon, but our institutional mandate forbids exceeding a 5% allocation per stock and requires sector neutrality."*
*   Segment 3 runs Convex Optimization (`cvxpy`) to balance the AI's signal against strict risk constraints, ultimately outputting the exact, safe allocation percentages for tomorrow's trades.

**Summary of the Flow:** 
`Raw Data (Seg 1)` ➡️ `Processed Z-Scores (Seg 2)` ➡️ `AI Predictions (Seg 4)` ➡️ `Risk-Managed Portfolio Weights (Seg 3)`
