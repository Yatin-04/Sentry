# Interview Prep: Backtest Engine & Metrics (Segment 5)

This document covers the execution lifecycle, metrics math, and the edge cases handled during the historical simulation.

## 1. Portfolio Drift Simulation

**What we did:** Instead of assuming weights remain static throughout the month, we accurately drifted the portfolio weights daily based on price movements in `backtester.py`.

> [!IMPORTANT]
> **Interview Question:** *What is 'Portfolio Drift' and why is it a critical bug if a backtester ignores it?*
> 
> **Your Answer:** 
> "In institutional asset management, a portfolio is not rebalanced every single second. When you allocate 5% to Nvidia at the start of the month and it rallies 30% while the rest of the market is flat, Nvidia now makes up ~6.5% of your portfolio on day 21. 
> If a backtester assumes weights remain exactly 5.0% every day, it implicitly assumes you are executing cost-free micro-rebalancing trades every single day. My backtester calculates exact daily price relatives and computes the drifted weights at month-end, ensuring that next month's turnover constraint starts from the true drifted portfolio state."

## 2. Explicit Transaction Cost Penalty

**What we did:** Deducted 10 basis points (0.10%) per dollar of two-way turnover from the cash value at every rebalance.

> [!WARNING]
> **Interview Question:** *Why did you hardcode a transaction cost penalty? Can't you just evaluate the gross returns?*
> 
> **Your Answer:** 
> "Backtests without transaction costs are fantasy. A strategy that generates a 15% return with 90% monthly turnover might actually lose money in real execution after commissions, exchange fees, and bid-ask slippage. I enforced a strict 10 bps friction penalty to ensure the ML isn't just chasing noise that gets eaten by trading fees."

## 3. The Equal-Weight Benchmark Decision

**What we did:** Benchmarked the strategy against an Equal-Weighted universe (1/N) instead of a market-cap weighted index like SPY.

> [!TIP]
> **Interview Question:** *Why did you benchmark against an Equal-Weighted universe instead of the standard S&P 500 Market-Cap Weighted index?*
> 
> **Your Answer:** 
> "Because our optimizer strictly caps individual stock weights at 5%, our portfolio can never hold the massive 30% concentration that the top 5 tech companies have in the cap-weighted S&P 500. If tech rallies massively, a cap-weighted benchmark's performance is driven purely by mega-cap concentration, not factor alpha. Benchmarking against an Equal-Weighted universe isolates whether our Multi-Factor + ML strategy genuinely selected better stocks than a naive baseline, removing market-cap distortion."

## 4. Unrealistic Sharpe Ratios

**What we did:** We implemented a rigorous cross-sectional calculation that resulted in a realistic ~1.36 Sharpe Ratio.

> [!CAUTION]
> **Interview Question:** *If your backtest produces a Sharpe Ratio of 3.5 on equity factor data, would you deploy it to live trading?*
> 
> **Your Answer:** 
> "No, I would immediately suspect a bug. In equity factor investing, a genuine net Sharpe Ratio between 0.8 and 1.5 is realistic and excellent. A Sharpe Ratio > 3.0 on monthly equity factors almost always indicates Look-Ahead Bias (e.g., target forward returns leaking into features, or survivorship bias). I would immediately audit the target alignment and verify transaction cost deductions."
