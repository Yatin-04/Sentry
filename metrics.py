import pandas as pd
import numpy as np

def calculate_annualized_return(daily_returns):
    """
    Calculates the Compound Annual Growth Rate (CAGR).
    Assumes daily_returns is a pandas Series of daily percentage returns.
    """
    # Convert returns to wealth index
    wealth_index = (1 + daily_returns).cumprod()
    if len(wealth_index) == 0:
        return 0.0
        
    total_return = wealth_index.iloc[-1] - 1
    # 252 trading days in a year
    years = len(daily_returns) / 252.0
    
    # CAGR formula: (Final Value / Initial Value) ^ (1/Years) - 1
    cagr = (1 + total_return) ** (1 / years) - 1
    return cagr

def calculate_annualized_volatility(daily_returns):
    """
    Calculates annualized volatility.
    """
    return daily_returns.std() * np.sqrt(252)

def calculate_sharpe_ratio(daily_returns, risk_free_rate=0.02):
    """
    Calculates the Sharpe Ratio (Risk-Adjusted Return).
    Assuming a static 2% risk-free rate for simplicity in this prototype.
    """
    ann_ret = calculate_annualized_return(daily_returns)
    ann_vol = calculate_annualized_volatility(daily_returns)
    
    if ann_vol == 0:
        return 0.0
        
    return (ann_ret - risk_free_rate) / ann_vol

def calculate_max_drawdown(daily_returns):
    """
    Calculates the Maximum Drawdown (deepest drop from a peak).
    """
    wealth_index = (1 + daily_returns).cumprod()
    
    # Calculate the running maximum
    running_max = wealth_index.cummax()
    
    # Calculate the drawdown from the running maximum
    drawdown = (wealth_index - running_max) / running_max
    
    # Max drawdown is the minimum value (most negative) of the drawdown series
    return drawdown.min()

def calculate_information_ratio(strategy_returns, benchmark_returns):
    """
    Calculates the Information Ratio (Active Return / Active Risk).
    How much extra return did we generate per unit of extra risk taken?
    """
    # Align dates
    df = pd.concat([strategy_returns, benchmark_returns], axis=1).dropna()
    df.columns = ['Strategy', 'Benchmark']
    
    active_returns = df['Strategy'] - df['Benchmark']
    
    ann_active_return = active_returns.mean() * 252
    ann_active_vol = active_returns.std() * np.sqrt(252)
    
    if ann_active_vol == 0:
        return 0.0
        
    return ann_active_return / ann_active_vol

def generate_performance_report(strategy_returns, benchmark_returns):
    """
    Generates a tear sheet of all performance metrics.
    """
    metrics = {
        'Annualized Return': calculate_annualized_return(strategy_returns),
        'Annualized Volatility': calculate_annualized_volatility(strategy_returns),
        'Sharpe Ratio': calculate_sharpe_ratio(strategy_returns),
        'Max Drawdown': calculate_max_drawdown(strategy_returns),
        'Information Ratio': calculate_information_ratio(strategy_returns, benchmark_returns)
    }
    
    bench_metrics = {
        'Annualized Return': calculate_annualized_return(benchmark_returns),
        'Annualized Volatility': calculate_annualized_volatility(benchmark_returns),
        'Sharpe Ratio': calculate_sharpe_ratio(benchmark_returns),
        'Max Drawdown': calculate_max_drawdown(benchmark_returns),
        'Information Ratio': 0.0 # Benchmark has 0 active risk against itself
    }
    
    report = pd.DataFrame([metrics, bench_metrics], index=['Sentry ML Strategy', 'Equal-Weight Benchmark'])
    return report.T # Transpose for better readability
