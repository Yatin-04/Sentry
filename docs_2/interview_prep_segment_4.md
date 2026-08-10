# Interview Prep: ML Alpha Generation (Segment 4)

This document captures the key ML engineering decisions and potential interview cross-questions from building the XGBoost Alpha prediction system.

## 1. On-The-Spot Training vs Production

**What we did:** In `alpha_model.py`, we implemented a loop that trains a brand new XGBoost model on historical data right before predicting each month's return.

> [!CAUTION]  
> **Interview Question:** *Do real Wall Street hedge funds train a massive AI model at 9:15 AM right before the market opens?*
> 
> **Your Answer:** 
> "No, live trading and backtesting operate fundamentally differently. 
> In **Live Trading (Production)**, you train the model over the weekend on heavy compute clusters, save it as a serialized `.pkl` file, and on Monday morning you just pass the live data into it for instant inference.
> However, my project is a **Backtesting Simulation**. When simulating 6 years of history, I had to artificially recreate that 'weekend retraining' effect. That is why the code trains 'on the spot' inside the loop—it simulates the periodic, walk-forward retraining that would have happened historically. This prevents concept drift."

## 2. Walk-Forward Expanding Window

**What we did:** We strictly enforced a time-aware split (`X_train.index < rebalance_date`), avoiding `train_test_split`.

> [!TIP]  
> **Interview Question:** *How did you ensure your Machine Learning model doesn't suffer from Look-Ahead Bias? How much data goes into the XGBoost training loop?*
> 
> **Your Answer:** 
> "I strictly enforced **Walk-Forward Expanding Window Validation**. I never used standard K-Fold Cross Validation, because those randomly shuffle time-series data, leaking future knowledge into the past. 
> The model uses an **Expanding Window**, meaning it ingests the *entire* past dataset available before the prediction date. If predicting for 2024, it trains on 2018 through 2023. The AI never forgets long-term history while learning recent trends."

## 3. The 2-Year Rule (Burn-in)

**What we did:** We defined `ML_MIN_TRAIN_DAYS = 504` in `config.py` as a fallback boundary.

> [!WARNING]  
> **Interview Question:** *What happens when you first launch the backtester in 2018 and have no historical data?*
> 
> **Your Answer:** 
> "The '2-year rule' (`ML_MIN_TRAIN_DAYS = 504`) is a **Minimum Burn-in Condition**. It tells the AI: 'Refuse to predict and use the fallback system if you have less than 2 years of history, because you will overfit.' During this time, the system uses a fallback heuristic (equal-weighting the Z-scores). Once the threshold is crossed, it seamlessly activates the XGBoost engine."

## 4. Predicting Ranks vs Returns

**What we did:** We trained XGBoost to predict the *relative rank* of stock returns, rather than the exact dollar return.

> [!IMPORTANT]  
> **Interview Question:** *Why did you set your XGBoost objective to predict 'Rank' instead of exact percentage return?*
> 
> **Your Answer:** 
> "Portfolio optimization is fundamentally a cross-sectional ranking problem, not a time-series forecasting problem. The optimizer doesn't care if Apple will return exactly 5.2% and Tesla 4.1%. It only cares that Apple will out-perform Tesla so it can overweight Apple. Predicting exact noisy returns in finance is mathematically near-impossible, but predicting relative ranking is statistically much more stable."
