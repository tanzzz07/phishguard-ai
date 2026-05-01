"""
PhishGuard AI - SHAP Explainability Module
============================================
Uses SHAP TreeExplainer to explain XGBoost predictions.
Generates waterfall plots and human-readable feature importance text.
"""

import os, sys, io, base64, joblib
import numpy as np
import shap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MODEL_PATH, FEATURE_NAMES


_model = None
_explainer = None


def _load():
    """Lazy-load model and SHAP explainer."""
    global _model, _explainer
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        _explainer = shap.TreeExplainer(_model)
    return _model, _explainer


def explain(features_array):
    """
    Compute SHAP values for a single prediction.

    Args:
        features_array: list or 1-D array of feature values (length 15).

    Returns:
        dict with 'shap_values' (list), 'base_value' (float),
        'feature_contributions' (list of dicts sorted by abs impact).
    """
    _, explainer = _load()
    arr = np.array(features_array).reshape(1, -1)
    shap_values = explainer.shap_values(arr)
    sv = shap_values[0]
    base_value = float(explainer.expected_value)

    contributions = []
    for i, name in enumerate(FEATURE_NAMES):
        # Only include lexical features in the contributions list for interpretability
        if name.startswith("emb_"):
            continue
            
        contributions.append({
            "feature": name,
            "value": float(features_array[i]),
            "shap_value": float(sv[i]),
        })
    contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

    return {
        "shap_values": [float(v) for v in sv],
        "base_value": base_value,
        "feature_contributions": contributions,
    }


def get_explanation_text(explanation: dict) -> str:
    """
    Generate human-readable text from SHAP explanation.

    Args:
        explanation: dict returned by explain().

    Returns:
        Multi-line string describing top feature contributions.
    """
    contribs = explanation["feature_contributions"]
    lines = ["Top features influencing the prediction:\n"]
    for c in contribs[:7]:
        direction = "INCREASES" if c["shap_value"] > 0 else "DECREASES"
        name = c["feature"].replace("_", " ").title()
        lines.append(
            f"  - {name} = {c['value']:.0f} → {direction} phishing risk "
            f"(impact: {c['shap_value']:+.4f})"
        )
    return "\n".join(lines)

if __name__ == "__main__":
    from utils.feature_extraction import extract_features_array
    test_url = "http://192.168.1.1/login/secure-bank/verify?user=admin"
    print(f"Testing SHAP on: {test_url}")
    feats = extract_features_array(test_url)
    exp = explain(feats)
    print(get_explanation_text(exp))
