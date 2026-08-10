import pandas as pd
import numpy as np
import xgboost as xgb
from factor_utils import cross_sectional_zscore
from config import ML_MIN_TRAIN_DAYS, ML_XGB_MAX_DEPTH, ML_XGB_LEARNING_RATE, ML_XGB_ESTIMATORS

def equal_weight_alpha_fallback(factors_df):
    """
    Tier-4 Safety Mechanism:
    If the Machine Learning model fails, diverges, or throws errors,
    we fallback to the safe, standard equal-weighted composite Z-score.
    We just take the average of Value, Quality, Momentum, and LowVol.
    """
    print("Executing ML Fallback: Using Equal-Weighted Z-Scores")
    factors = ['Value', 'Quality', 'Momentum', 'LowVol']
    composite = factors_df[factors].mean(axis=1)
    return cross_sectional_zscore(composite).fillna(0)

def prepare_ml_data(factor_scores, forward_returns):
    """
    Merges historical factor scores (X) with their corresponding future returns (Y).
    Critically, we convert the raw forward returns into a cross-sectional percentile rank.
    We don't care about predicting if a stock will go up 5% or 7%.
    We only care about predicting its RANK relative to other stocks.
    """
    # Join factors with returns
    ml_data = factor_scores.copy()
    ml_data['Target_Return'] = forward_returns.stack()
    
    # Drop rows where we don't have a future return (e.g. the very last month of our dataset)
    ml_data = ml_data.dropna(subset=['Target_Return'])
    
    # Convert absolute returns to cross-sectional ranks (0 to 1) per date
    ml_data['Target_Rank'] = ml_data.groupby(level='Date')['Target_Return'].rank(pct=True)
    
    return ml_data

def train_and_predict_walk_forward(ml_data, prediction_date):
    """
    Walk-Forward Expanding Window Model:
    Trains an XGBoost model strictly on data BEFORE the prediction_date to prevent look-ahead bias.
    Predicts the Alpha ranking for the stocks ON the prediction_date.
    """
    # 1. Filter training data strictly to past dates
    train_data = ml_data[ml_data.index.get_level_values('Date') < prediction_date]
    
    # Check if we have enough historical data to safely train a model
    unique_train_dates = train_data.index.get_level_values('Date').nunique()
    if unique_train_dates < (ML_MIN_TRAIN_DAYS / 21): # Roughly 24 months
        print(f"[{prediction_date.strftime('%Y-%m-%d')}] Insufficient ML training history ({unique_train_dates} months). Triggering Fallback.")
        return None
        
    # 2. Extract X (features) and Y (Target Rank)
    features = ['Value', 'Quality', 'Momentum', 'LowVol']
    X_train = train_data[features]
    y_train = train_data['Target_Rank']
    
    # 3. Train the XGBoost Model
    # We use shallow trees to prevent the model from memorizing noise
    model = xgb.XGBRegressor(
        n_estimators=ML_XGB_ESTIMATORS,
        max_depth=ML_XGB_MAX_DEPTH,
        learning_rate=ML_XGB_LEARNING_RATE,
        objective='reg:squarederror', # Predicting the rank percentile directly
        random_state=42,
        n_jobs=-1
    )
    
    try:
        model.fit(X_train, y_train)
    except Exception as e:
        print(f"[{prediction_date.strftime('%Y-%m-%d')}] XGBoost training failed: {e}")
        return None
        
    # 4. Predict on the current date
    # Get the features for the specific day we want to trade on
    current_day_data = ml_data[ml_data.index.get_level_values('Date') == prediction_date]
    
    if current_day_data.empty:
        return None
        
    X_test = current_day_data[features]
    
    # Predict the expected future rank (Alpha)
    predictions = model.predict(X_test)
    
    # Return as a pandas Series indexed by Ticker
    tickers = current_day_data.index.get_level_values('Ticker')
    alpha_scores = pd.Series(predictions, index=tickers)
    
    # Standardize predictions to mean 0, std 1
    return cross_sectional_zscore(alpha_scores).fillna(0)

def generate_ml_alpha(factor_scores, forward_returns, prediction_date):
    """
    Master function for Segment 4. 
    Attempts to generate ML-driven alpha. If it fails due to lack of data or model crash,
    it automatically falls back to the safe equal-weighted alpha.
    """
    ml_data = prepare_ml_data(factor_scores, forward_returns)
    
    alpha_scores = train_and_predict_walk_forward(ml_data, prediction_date)
    
    if alpha_scores is None or alpha_scores.empty or alpha_scores.isna().all():
        # Fallback mechanism
        current_factors = factor_scores[factor_scores.index.get_level_values('Date') == prediction_date]
        if not current_factors.empty:
            return equal_weight_alpha_fallback(current_factors)
        else:
            return pd.Series(dtype=float)
            
    return alpha_scores
