# Segment 4: Interview Prep & Ambiguities

This document covers the highly scrutinized interview questions for the XGBoost Alpha Model, specifically addressing the ambiguity between live trading, backtesting, and look-ahead bias.

## The Ambiguity: "On-The-Spot Training"

This is the most confusing part for beginners and a prime interview topic for quantitative engineering roles.

> [!CAUTION]  
> **Interview Question:** *I see your code trains a new XGBoost model inside a loop before every prediction. Do real Wall Street hedge funds train a massive AI model at 9:15 AM right before the market opens?*
> 
> **Your Answer:** 
> "No, live trading and backtesting operate fundamentally differently. 
> 
> In **Live Trading (Production)**, you never train 'on the spot' during market hours. That is computationally slow and carries immense execution risk. You train the model over the weekend on heavy compute clusters, save it as a serialized `.pkl` file, and on Monday morning you just pass the live data into it for instant inference.
> 
> However, my project is a **Backtesting Simulation**. When we simulate 6 years of history in 10 seconds, we have to artificially recreate that 'weekend retraining' effect. That is why my code trains 'on the spot' inside the loop—it is simulating the periodic, walk-forward retraining that would have happened historically. This prevents concept drift while avoiding look-ahead bias."

---

## Important Interview Defenses

> [!IMPORTANT]  
> **Interview Question:** *Why did you set your XGBoost objective to predict 'Rank' (`reg:squarederror` on percentiles) instead of predicting the exact percentage stock return?*
> 
> **Your Answer:** 
> "Portfolio optimization is fundamentally a cross-sectional ranking problem, not a time-series forecasting problem. The optimizer doesn't care if Apple will return exactly 5.2% and Tesla 4.1%. It only cares that Apple will out-perform Tesla so it can overweight Apple. Predicting exact noisy returns in finance is mathematically near-impossible, but predicting relative ranking is statistically much more stable."

> [!TIP]  
> **Interview Question:** *How did you ensure your Machine Learning model doesn't suffer from Look-Ahead Bias?*
> 
> **Your Answer:** 
> "I strictly enforced **Walk-Forward Expanding Window Validation**. I never used standard `train_test_split` or K-Fold Cross Validation, because those randomly shuffle time-series data, leaking future knowledge into the past. In my `train_and_predict_walk_forward` function, I explicitly filter the training data index to be strictly less than (`<`) the prediction date. The model predicting Jan 2020 has zero mathematical access to Feb 2020 data."

> [!WARNING]  
> **Interview Question:** *If your XGBoost model learns that Momentum is the only thing that matters, your optimizer might put 100% of the money into 20 tech stocks. How do you prevent that?*
> 
> **Your Answer:** 
> "This is why Segment 4 (Alpha Generation) and Segment 3 (Portfolio Optimization) are strictly separated. Even if the ML model screams to buy only 20 tech stocks, the predictions must pass through the `cvxpy` Convex Optimizer. The optimizer strictly enforces the `SECTOR_DEVIATION_CAP` (±5% sector neutrality) and `MAX_POSITION_SIZE` (5%). The ML provides the *signal*, but the Optimizer controls the *risk*."

> [!TIP]
> **Interview Question:** *How much data goes into the XGBoost training loop? Does it only use the most recent 2 years, or the entire past? Explain Expanding vs Rolling Windows.*
> 
> **Your Answer:**
> "The model uses an **Expanding Window**, meaning it ingests the *entire* past dataset available before the prediction date. If predicting for 2024, it trains on 2018 through 2023. The AI never forgets long-term history while learning recent trends. 
> The '2-year rule' in my code (`ML_MIN_TRAIN_DAYS = 504`) is merely a **Minimum Burn-in Condition**. It tells the AI: 'Refuse to predict and use the fallback system if you have less than 2 years of history, because you will overfit.' Once that 2-year threshold is crossed, it uses all cumulative historical data for the rest of its lifecycle."
