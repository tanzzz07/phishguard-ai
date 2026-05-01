"""
PhishGuard AI - Model Training Script
=======================================
Trains an XGBoost classifier on the phishing URL dataset.

Usage:
    python model/train_model.py
"""

import os, sys, numpy as np, pandas as pd, joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, classification_report, confusion_matrix)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATASET_PATH, MODEL_PATH, MODEL_DIR, FEATURE_NAMES, XGB_PARAMS


def load_dataset():
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset not found at: {DATASET_PATH}")
        print("Run `python data/generate_dataset.py` first.")
        sys.exit(1)
    df = pd.read_csv(DATASET_PATH)
    print(f"Loaded dataset: {len(df)} samples")
    print(f"  Phishing: {(df['label']==1).sum()} | Legitimate: {(df['label']==0).sum()}")
    return df[FEATURE_NAMES].values, df["label"].values


def train_model(X_train, y_train):
    n_pos = np.sum(y_train == 1)
    n_neg = np.sum(y_train == 0)
    params = XGB_PARAMS.copy()
    params["scale_pos_weight"] = n_neg / n_pos if n_pos > 0 else 1.0
    print(f"\nTraining XGBoost...")
    model = XGBClassifier(**params)
    model.fit(X_train, y_train, eval_set=[(X_train, y_train)], verbose=False)
    return model


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    print(f"\n{'='*60}")
    print(f"MODEL EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"  Accuracy:  {acc:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall:    {rec:.4f}")
    print(f"  F1-Score:  {f1:.4f}")
    print(f"  AUC-ROC:   {auc:.4f}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Legitimate", "Phishing"]))
    cm = confusion_matrix(y_test, y_pred)
    print(f"Confusion Matrix: TN={cm[0][0]} FP={cm[0][1]} FN={cm[1][0]} TP={cm[1][1]}")
    importances = model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    print(f"\nTop Feature Importances:")
    for i in range(min(10, len(FEATURE_NAMES))):
        idx = sorted_idx[i]
        print(f"  {i+1}. {FEATURE_NAMES[idx]:30s} = {importances[idx]:.4f}")
    return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "auc_roc": auc}


if __name__ == "__main__":
    print("="*70)
    print("PhishGuard AI - XGBoost Model Training")
    print("="*70)
    X, y = load_dataset()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"\nTrain: {len(X_train)} | Test: {len(X_test)}")
    model = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to: {MODEL_PATH}")
    print("="*70)
