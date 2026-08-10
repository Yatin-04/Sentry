# Interview Prep: Factor Engineering (Segment 2)

This document captures the mathematical logic and interview defensibility for the factors and the target variable.

## 1. Z-Scoring & Winsorization

**What we did:** Before combining factors (like P/E and momentum), we clipped extreme outliers (winsorized at 1% and 99%) and calculated the cross-sectional z-score.

> [!IMPORTANT]  
> **Interview Question:** *Why do you z-score factors before combining them, and why cross-sectionally?*
> 
> **Your Answer:** 
> "Factors are on completely different scales—a P/E ratio of 15 cannot be mathematically added to a return of 0.20. By calculating the cross-sectional z-score, I force every factor into a standardized normal distribution with a mean of 0 and a standard deviation of 1. A score of +2.0 means it is 2 standard deviations better than the market average for that specific day. 
> I do this *cross-sectionally* (comparing stocks to each other on the same day) rather than *longitudinally* (comparing a stock to its own history) because portfolio optimization is a cross-sectional problem: we want to know what to buy *today* relative to the other options available *today*."

## 2. The Value Factor (E/P & B/P)

**What we did:** Used Earnings Yield (E/P) instead of P/E.

> [!TIP]  
> **Interview Question:** *Why did you use Earnings Yield instead of the standard P/E ratio?*
> 
> **Your Answer:** 
> "Using P/E is dangerous in an automated pipeline because it breaks when earnings are zero (divide by zero error) and is mathematically non-linear when earnings are negative. By inverting it to Earnings Yield (E/P), zero earnings simply equals a 0% yield, and negative earnings equals a negative yield. It handles edge cases gracefully without requiring complex `if/else` logic in the pipeline."

## 3. The Quality Factor (ROE & Debt)

**What we did:** Combined high ROE with low Debt-to-Equity. 

> [!TIP]  
> **Interview Question:** *How do you combine a factor where 'higher is better' (ROE) with one where 'lower is better' (Debt)?*
> 
> **Your Answer:** 
> "After winsorizing and z-scoring both metrics independently, I simply negate the Debt z-score before adding them together. This ensures that low debt contributes positively to the final Quality composite score."

## 4. The Momentum Factor (12-1 Month)

**What we did:** Calculated the 12-month return, explicitly skipping the most recent 1 month (the "12-1 month" momentum factor).

> [!WARNING]  
> **Interview Question:** *Why do you skip the most recent month when calculating Momentum? Why not just use the 12-month return?*
> 
> **Your Answer:** 
> "Academic literature (Jegadeesh and Titman) and industry practice show that equities exhibit momentum over the medium term (6-12 months) but exhibit *mean-reversion* over the short term (1 month). If a stock spikes 20% in the last 2 weeks, it is highly likely to revert slightly in the next 2 weeks. Skipping the most recent 21 trading days strips out this short-term noise and isolates the true medium-term trend."

## 5. The Target Variable (Forward Returns)

**What we did:** Set the `Y` variable for our ML model to be the return over the *next* 21 trading days (1 month), looking forward from the rebalance date.

> [!CAUTION]  
> **Interview Question:** *How did you ensure your ML model doesn't suffer from look-ahead bias?*
> 
> **Your Answer:** 
> "The most common mistake is misaligning the features (X) and the target (Y). In my `factor_utils.py`, the `compute_forward_returns` function specifically uses `.shift(-21)`. This means that for a rebalance date of Jan 31st, the features X are calculated using *strictly* backward-looking data up to Jan 31st, but the target label Y is the return from Jan 31st to Feb 28th. The model is trained to predict the future, not the past."

## 6. The Missing Data Trap (Z-Score Math)

**What we faced:** When computing factors, some stocks inevitably have missing data (e.g. no P/E ratio). A junior quant might write `.fillna(data.median())`. 

> [!WARNING]  
> **Interview Question:** *How do you handle missing fundamental data for a specific stock when calculating z-scores?*
> 
> **Your Answer:** 
> "If you calculate the z-score first, and *then* fill missing values, you must fill them with `0`, not the median of the raw data. Since a z-score has a mean of 0, assigning 0 simply means 'assume this stock is exactly average for this factor.' If you accidentally fill a missing z-score with the raw median (e.g. 15.5 for a P/E ratio), you are mathematically telling the model that stock is 15 standard deviations above the mean, which will destroy the optimizer."

## 7. The Stock Split Trap

**What we faced:** `yfinance` returns both `Close` and `Adj Close`. 

> [!CAUTION]  
> **Interview Question:** *When calculating Momentum and Volatility, which price column do you use and why?*
> 
> **Your Answer:** 
> "You must rigorously use `Adjusted Close`. If Apple executes a 4-for-1 stock split, the raw `Close` price drops by 75% overnight. If my momentum factor uses the raw `Close` price, it will think Apple just suffered a catastrophic 75% crash and will short the stock. `Adj Close` retroactively adjusts historical prices so the percentage returns reflect true economic reality."

## 8. The Calendar vs. Trading Days Trap

**What we faced:** In `compute_forward_returns`, we used `.shift(-21)`.

> [!TIP]  
> **Interview Question:** *Why did you shift the dataframe by 21 rows to calculate a 1-month forward return, instead of just finding the exact calendar date one month in the future?*
> 
> **Your Answer:** 
> "Shifting by exact calendar dates (e.g. Jan 15 to Feb 15) is dangerous because Feb 15th might fall on a Saturday or a market holiday, throwing a KeyError. There are roughly 252 trading days in a year, which averages exactly 21 trading days per month. `.shift(-21)` reliably calculates the 1-month return along the contiguous trading day index, avoiding weekend alignment bugs."
