# Interview Prep: Data Pipeline (Segment 1)

This document captures the key decisions, bugs faced, and potential interview cross-questions from building the data pipeline. Review this before the BlackRock PMG interview.

## 1. The Universe Selection

**What we did:** Hardcoded a list of ~98 mega-cap S&P 500 stocks instead of dynamically pulling the current S&P 500 list or trying to use the full 500.

> [!IMPORTANT]  
> **Interview Question:** *Why did you only use 98 stocks, and why are they hardcoded instead of pulling the S&P 500 from Wikipedia?*
> 
> **Your Answer:** 
> "There are three reasons. 
> First, **Survivorship Bias**. If I pull the *current* S&P 500 and backtest it to 2018, I am only testing companies that survived and did well enough to stay in the index. I'm completely ignoring companies that went bankrupt or dropped out since 2018. By hardcoding a stable universe of 98 mega-caps (like Apple, Microsoft, JPM), the likelihood of index turnover within that specific sub-group is almost zero, which mitigates survivorship bias in a toy project.
> Second, **API Constraints**. Free APIs like `yfinance` frequently rate-limit or fail on 500-ticker batch downloads. 
> Third, **Compute Speed**. In the optimization phase, inverting a 100x100 covariance matrix is significantly faster than a 500x500 matrix, which allowed for faster iteration during this 17-hour build."

## 2. Dealing with API Failures (The FI & MMC bug)

**What we faced:** When pulling data, `yfinance` threw 404 errors for `FI` (Fiserv) and `MMC` (Marsh McLennan) and returned no data. We dropped them from the universe.

> [!WARNING]  
> **Interview Question:** *What happens in a production system if pricing data for a ticker is missing for a few days? Do you just drop the ticker?*
> 
> **Your Answer:** 
> "In this prototype, I dropped them because they failed completely on the initial bulk download. However, in a production system, dropping a ticker because of a missing day of data is dangerous—it forces an unmodeled liquidation of that position in the portfolio. 
> In production, you would implement a **forward-fill** (filling missing prices with the last known good price) up to a certain threshold (e.g., 3 days). If the data is missing beyond that threshold, you flag it for a data operations team to investigate, or you freeze trading on that name in the optimizer."

## 3. The Fundamental Data Trap (Look-Ahead Bias)

**What we did:** We pulled P/E, P/B, ROE, and Debt/Equity using `yfinance.Ticker().info` and saved it to a CSV.

> [!CAUTION]  
> **Interview Question:** *Are there any flaws in how you handle fundamental data for your Value and Quality factors?*
> 
> **Your Answer:** 
> "Yes, and I explicitly documented this as a known limitation in the README. `yfinance` only provides a **current snapshot** of fundamentals. It does not provide historical, point-in-time fundamentals. 
> This means if my backtest is calculating a Value score for Apple in 2019, it is accidentally using Apple's P/E ratio from 2026. This introduces massive **look-ahead bias**. 
> To do this properly at BlackRock, I would need a point-in-time database like Compustat or FactSet, which records exactly what the P/E was on that specific date in 2019, including revisions. For a 17-hour weekend project, the snapshot is a necessary compromise, but I wanted to make it clear I understand the difference."

## 4. The Cache Updating Mechanism

**What we did:** Initially, the cache would never update unless you manually deleted it. We upgraded it to a production-style **delta-append** logic.

> [!TIP]  
> **Interview Question:** *If I deploy your data pipeline and run it every day, does it download 8 years of data every single time?*
> 
> **Your Answer:** 
> "No, I built a delta-update mechanism. When the script runs, it checks the existing `price_data.parquet` file and finds the `max(Date)`. It then queries the Yahoo Finance API *only* for the missing days (the delta) between that max date and today. It then appends those new rows to the existing parquet file. This is how a production ETL pipeline should behave to minimize network overhead and API calls."

## 5. The Date Boundary Bug (Exclusive End Dates & Weekends)

**What we faced:** We wrote a delta-append script to fetch missing days. However, when we ran it on a Monday, it fetched nothing, appended nothing, and got stuck in a loop where it constantly thought it needed to fetch the missing weekend data.

> [!WARNING]  
> **Interview Question:** *When building automated data pipelines, what is a common bug you've encountered with date boundaries?*
> 
> **Your Answer:** 
> "A classic issue is handling exclusive vs. inclusive date parameters across weekends. In this project, `yfinance` treats the `end` date as exclusive. When I ran the script on Monday the 10th, it queried up to Sunday the 9th. Because the market was closed over the weekend, it found zero trading days, meaning the cache's max date never advanced past Friday the 7th. Every subsequent run triggered a delta-fetch because Friday < Monday. 
> To fix this, I engineered two safeguards: first, I dynamically added `+ 1 day` to the API request to force inclusivity. Second, I added a strict filter `delta_data.index > max_date` to discard any overlapping historical data the API might erroneously return, mathematically guaranteeing the cache only accepts strictly forward-moving data."
