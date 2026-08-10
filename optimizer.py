import numpy as np
import pandas as pd
import cvxpy as cp
from sklearn.covariance import LedoitWolf
from config import MAX_POSITION_SIZE, SECTOR_DEVIATION_CAP, MAX_TURNOVER, RISK_AVERSION

def make_closest_psd(matrix):
    """
    Mathematical Protection:
    Covariance matrices must be Positive Semi-Definite (PSD) for convex optimization.
    Even with Ledoit-Wolf, floating-point arithmetic can sometimes create tiny negative 
    eigenvalues (e.g., -1e-16), causing cvxpy to throw a DCPError.
    This function explicitly projects the matrix to the nearest PSD matrix.
    """
    # Symmetrize to fix tiny floating point asymmetries
    sym_matrix = (matrix + matrix.T) / 2
    
    # Eigenvalue decomposition
    eigval, eigvec = np.linalg.eigh(sym_matrix)
    
    # Clip negative eigenvalues to a tiny positive number
    eigval[eigval < 1e-8] = 1e-8
    
    # Reconstruct the matrix
    psd_matrix = eigvec @ np.diag(eigval) @ eigvec.T
    return psd_matrix

def estimate_covariance(returns_slice):
    """
    Estimates the covariance matrix using Ledoit-Wolf shrinkage.
    Shrinkage pulls the noisy sample covariance matrix toward a structured target,
    which is critical when N (stocks) is large relative to T (time periods).
    """
    clean_returns = returns_slice.dropna(how='all').fillna(0)
    
    lw = LedoitWolf()
    cov_matrix = lw.fit(clean_returns).covariance_
    
    # Annualize the covariance matrix (252 trading days)
    ann_cov_matrix = cov_matrix * 252
    
    # Rigorous PSD projection to prevent cvxpy solver crashes
    return make_closest_psd(ann_cov_matrix)

def get_sector_matrices(fundamentals_df, tickers):
    """
    Creates mapping matrices for sector neutrality constraints.
    """
    sectors = fundamentals_df.loc[tickers, 'Sector'].fillna('Unknown')
    unique_sectors = sectors.unique()
    
    num_sectors = len(unique_sectors)
    num_tickers = len(tickers)
    
    sector_matrix = np.zeros((num_sectors, num_tickers))
    for i, sector in enumerate(unique_sectors):
        sector_matrix[i, :] = (sectors == sector).astype(int)
        
    # Assume benchmark is equal-weighted across the universe for this prototype
    benchmark_weights = np.ones(num_tickers) / num_tickers
    benchmark_sector_weights = sector_matrix @ benchmark_weights
    
    return sector_matrix, benchmark_sector_weights

def heuristic_fallback_weights(alpha_scores, max_weight=MAX_POSITION_SIZE):
    """
    Safety Protection (Fallback Tier 3):
    If the convex optimizer mathematically cannot find a feasible solution 
    (which happens in violent market regimes), we MUST return a valid portfolio 
    rather than crashing the pipeline. 
    This assigns max_weight to the top N alpha scores until fully invested.
    """
    print("WARNING: All convex optimization attempts failed. Using heuristic fallback.")
    sorted_alpha = alpha_scores.sort_values(ascending=False)
    weights = pd.Series(0.0, index=alpha_scores.index)
    
    remaining_weight = 1.0
    for ticker in sorted_alpha.index:
        if remaining_weight <= 0:
            break
        alloc = min(max_weight, remaining_weight)
        weights[ticker] = alloc
        remaining_weight -= alloc
        
    return weights

def optimize_portfolio(alpha_scores, cov_matrix, current_weights, sector_matrix, benchmark_sector_weights):
    """
    Convex optimization using cvxpy with a multi-tier fallback system.
    """
    n = len(alpha_scores)
    w = cp.Variable(n)
    
    # We must explicitly wrap cov_matrix in cp.psd_wrap as a secondary guarantee for cvxpy
    risk_penalty = (RISK_AVERSION / 2) * cp.quad_form(w, cp.psd_wrap(cov_matrix))
    expected_alpha = alpha_scores.values @ w
    objective = cp.Maximize(expected_alpha - risk_penalty)
    
    # Base Constraints (Hard limits, never relaxed)
    base_constraints = [
        cp.sum(w) == 1,                      # Fully invested
        w >= 0,                              # Long only
        w <= MAX_POSITION_SIZE               # Position size cap
    ]
    
    # Sector Constraints
    sector_weights = sector_matrix @ w
    sector_constraints = [
        sector_weights <= benchmark_sector_weights + SECTOR_DEVIATION_CAP,
        sector_weights >= benchmark_sector_weights - SECTOR_DEVIATION_CAP
    ]
    
    # Turnover Constraints
    turnover_constraints = []
    if current_weights is not None:
        # L1 norm of weight changes <= max_turnover
        turnover_constraints = [cp.norm(w - current_weights, 1) <= MAX_TURNOVER]
        
    # --- TIER 1: Full Constraints ---
    prob = cp.Problem(objective, base_constraints + sector_constraints + turnover_constraints)
    try:
        prob.solve(solver=cp.ECOS)
    except Exception:
        pass # Fall through to Tier 2
        
    # --- TIER 2: Relax Turnover ---
    if prob.status not in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
        print("Tier 1 Optimization failed/infeasible. Relaxing turnover constraint...")
        prob = cp.Problem(objective, base_constraints + sector_constraints)
        try:
            prob.solve(solver=cp.ECOS)
        except Exception:
            pass
            
    # --- TIER 3: Relax Sector Bounds ---
    if prob.status not in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
        print("Tier 2 Optimization failed. Relaxing sector constraints...")
        prob = cp.Problem(objective, base_constraints + turnover_constraints)
        try:
            prob.solve(solver=cp.ECOS)
        except Exception:
            pass

    # --- TIER 4: Heuristic Fallback ---
    if prob.status not in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
        return heuristic_fallback_weights(alpha_scores)
        
    # Clean up small numerical noise (e.g. 1e-10) -> 0
    weights = np.array(w.value)
    if weights is None:
        return heuristic_fallback_weights(alpha_scores)
        
    weights[weights < 1e-4] = 0
    
    # Re-normalize to mathematically guarantee sum == 1.0
    weight_sum = np.sum(weights)
    if weight_sum > 0:
        weights = weights / weight_sum
    else:
        # Edge case protection
        return heuristic_fallback_weights(alpha_scores)
    
    return pd.Series(weights, index=alpha_scores.index)
