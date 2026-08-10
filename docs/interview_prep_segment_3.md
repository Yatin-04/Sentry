# Interview Prep: Portfolio Optimizer (Segment 3)

This is the most scrutinized part of a PMG interview. While alpha research is important, **portfolio construction** is the core competency of the Portfolio Management Group. Review this document to defend the convex optimization architecture.

## 1. Why Convex Optimization over Heuristics?

**What we did:** Used `cvxpy` (specifically the ECOS solver for Second-Order Cone Programming / Quadratic Programming) instead of just equal-weighting or z-score-weighting the stocks.

> [!IMPORTANT]  
> **Interview Question:** *Why did you use a complex solver like cvxpy instead of simply weighting the stocks by their factor z-scores?*
> 
> **Your Answer:** 
> "Heuristic weighting (like IC-weighting or z-score-weighting) cannot mathematically guarantee that constraints are met. If a PM says 'We cannot hold more than 5% of any stock, and we must remain sector-neutral,' heuristic weighting will violate those rules. Convex optimization allows us to define an exact objective function (maximize alpha minus risk) subject to strict, non-negotiable constraints. It provides a *provably optimal* solution. This is the same underlying mathematical architecture used by systems like BlackRock's Aladdin."

## 2. The Covariance Matrix & PSD Projection

**What we did:** Used Ledoit-Wolf shrinkage to estimate covariance, and wrote a custom function to project it to the nearest Positive Semi-Definite (PSD) matrix.

> [!WARNING]  
> **Interview Question:** *What happens when you invert a sample covariance matrix with 100 stocks using only 1 year of data?*
> 
> **Your Answer:** 
> "With N=100 and T=252, the sample covariance matrix contains massive estimation error and extreme condition numbers, meaning the optimizer will 'error-maximize' and take huge, unstable bets. To solve this, I used **Ledoit-Wolf shrinkage**, which pulls the noisy sample matrix toward a structured target, creating a stable, well-conditioned matrix. 
> Furthermore, `cvxpy` mathematically requires the matrix to be strictly Positive Semi-Definite (PSD). Due to floating-point arithmetic on computers, even a valid matrix can compute with an eigenvalue of `-1e-16`, which will crash the solver with a `DCPError`. I built a strict mathematical protection: `make_closest_psd()`, which runs eigenvalue decomposition, clips negative roots to `1e-8`, and rebuilds the matrix, guaranteeing the pipeline never crashes."

## 3. The 4-Tier Fallback System (Handling Infeasibility)

**What we did:** Built a nested `try/except` block to relax constraints if the solver fails.

> [!CAUTION]  
> **Interview Question:** *During the March 2020 crash, your optimizer realizes it cannot satisfy the turnover constraint AND the sector-neutrality constraint simultaneously. The problem is mathematically infeasible. What does your code do?*
> 
> **Your Answer:** 
> "A naive script would throw an `Infeasible` exception and return no portfolio, halting live trading. I engineered a 4-tier fallback system. 
> 1. It first attempts to solve with all constraints. 
> 2. If it fails, it relaxes the *Turnover* constraint (it is better to pay higher transaction costs than to miss the market). 
> 3. If that fails, it relaxes the *Sector* constraint. 
> 4. If convex optimization completely fails, it hits a mathematical fallback: it bypasses the solver and assigns equal heuristic weights to the top alpha scores. The system is designed to *always* return a valid portfolio."

## 4. Numerical Noise and Micro-Trades

**What we did:** Added logic to force any weight under 0.0001 (1 basis point) to zero.

> [!TIP]  
> **Interview Question:** *Optimizers often return weights like `1.45e-11`. What happens if you pass that directly to an execution desk?*
> 
> **Your Answer:** 
> "You will incur massive fixed transaction costs (ticket charges) for trading fractions of a penny, and the traders will be furious. Before my optimizer returns the weights, it explicitly zeros out any weight under 1 basis point (0.01%). It then rigorously re-normalizes the remaining weights to ensure they sum to exactly 1.0, with a division-by-zero safeguard in case of total mathematical collapse."

## 5. Known Flaws & Limitations (State These Proactively)

If asked about the weaknesses of your optimizer, or what you would improve with more time, cite these specific flaws:

1. **Transaction Costs are a Proxy:** The optimizer restricts turnover (using an L1 norm penalty: `cp.norm(w - current_weights, 1) <= max_turnover`). However, it does not model *actual* transaction costs (slippage, bid-ask spread, market impact). In a true BlackRock system, TC is modeled as a non-linear penalty in the objective function.
2. **Static Risk Aversion:** The `RISK_AVERSION` parameter ($\lambda$) is hardcoded to `1.0`. In reality, this should be dynamically scaled based on the forecasted volatility regime.
3. **No Factor Risk Model:** We used a shrunk historical covariance matrix. Production systems (like Barra or Axioma) use fundamental factor risk models (where risk is decomposed into Style, Industry, and Idiosyncratic risk) which forecast future covariance much better than historical prices do.
