"""
PhishGuard AI - Flask Backend (Phase 1 - Lightweight Deployment)
"""

import os
import numpy as np
import joblib
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Import feature extraction

from utils.feature_extraction import extract_features, extract_features_array

# ── Flask App Setup ─────────────────────────────────────────────

app = Flask(**name**, static_folder="static", template_folder="templates")
CORS(app)

# ── Load Model ──────────────────────────────────────────────────

MODEL_PATH = "model.pkl"
_model = None

def get_model():
global _model
if _model is None:
if not os.path.exists(MODEL_PATH):
raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
_model = joblib.load(MODEL_PATH)
return _model

# ── Routes ──────────────────────────────────────────────────────

@app.route("/")
def index():
return "PhishGuard AI is running"

@app.route("/api/health", methods=["GET"])
def health():
return jsonify({"status": "ok", "service": "PhishGuard AI"})

@app.route("/api/analyze", methods=["POST"])
def analyze():
try:
data = request.get_json()

```
    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' field"}), 400

    url = data["url"].strip()
    if not url:
        return jsonify({"error": "URL cannot be empty"}), 400

    # 1. Feature extraction
    features_dict = extract_features(url)
    features_array = extract_features_array(url)

    # 2. Model prediction
    model = get_model()
    features_np = np.array(features_array).reshape(1, -1)

    prediction_proba = model.predict_proba(features_np)[0]
    pred_class = int(model.predict(features_np)[0])

    prediction = "Phishing" if pred_class == 1 else "Legitimate"
    confidence = float(prediction_proba[pred_class])

    # 3. Response
    return jsonify({
        "url": url,
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "features": features_dict,
        "note": "Advanced explanations (SHAP/RAG) disabled in this version"
    })

except Exception as e:
    return jsonify({"error": str(e)}), 500
```

# ── Run Locally ─────────────────────────────────────────────────

if **name** == "**main**":
app.run(host="0.0.0.0", port=5000, debug=True)
