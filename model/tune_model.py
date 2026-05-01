"""
PhishGuard AI - Model Tuning Script
======================================
Tunes XGBoost hyperparameters using RandomizedSearchCV on a subset of the dataset.
"""

import os, sys, numpy as np, pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from scipy.stats import randint, uniform

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATASET_PATH, FEATURE_NAMES

def load_data_subset(frac=0.25):
    """Load a stratified subset of the dataset for faster tuning."""
    print(f"Loading {frac*100}% of the dataset for tuning...")
    df = pd.read_csv(DATASET_PATH)
    _, df_subset = train_test_split(df, test_size=frac, random_state=42, stratify=df["label"])
    print(f"Subset loaded: {len(df_subset)} samples")
    return df_subset[FEATURE_NAMES].values, df_subset["label"].values

def tune_xgboost():
    X, y = load_data_subset(frac=0.25)
    
    n_pos = np.sum(y == 1)
    n_neg = np.sum(y == 0)
    scale_pos_weight = n_neg / n_pos if n_pos > 0 else 1.0

    # Define hyperparameter search space
    param_dist = {
        'n_estimators': randint(100, 300),
        'max_depth': randint(4, 10),
        'learning_rate': uniform(0.01, 0.2),
        'subsample': uniform(0.6, 0.4),
        'colsample_bytree': uniform(0.6, 0.4),
    }

    base_model = XGBClassifier(
        objective='binary:logistic',
        scale_pos_weight=scale_pos_weight,
        eval_metric='logloss',
        random_state=42,
        n_jobs=-1
    )

    print("\nStarting RandomizedSearchCV (3 folds, 10 iterations)...")
    search = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=param_dist,
        n_iter=10,
        scoring='f1',
        cv=3,
        verbose=2,
        random_state=42,
        n_jobs=1 # xgboost n_jobs=-1 will handle parallelization
    )
    
    search.fit(X, y)
    
    print("\n" + "="*50)
    print("Tuning Completed!")
    print("Best F1-Score:", search.best_score_)
    print("Best Parameters:")
    for k, v in search.best_params_.items():
        if isinstance(v, float):
            print(f"  '{k}': {v:.4f},")
        else:
            print(f"  '{k}': {v},")
    print("="*50)
    print("Please manually update config.py with these parameters.")

if __name__ == "__main__":
    tune_xgboost()
