"""
PhishGuard AI - Flask Backend
===============================
Main application server with API endpoints for URL analysis.

Endpoints:
    GET  /             → Serve dashboard
    POST /api/analyze  → Analyze a URL (returns full JSON)
    GET  /api/health   → Health check
"""

import os, sys, traceback
import numpy as np
import joblib
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (MODEL_PATH, FLASK_HOST, FLASK_PORT, FLASK_DEBUG,
                    FEATURE_NAMES, STATIC_DIR)
from utils.feature_extraction import extract_features, extract_features_array
from utils.shap_explainer import explain, get_explanation_text
##from rag.vector_store import search as rag_search, build_index, _load_index, get_embedding

# ── Flask App Setup ──────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Load ML model at startup
_model = None

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Run `python model/train_model.py` first."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main dashboard page."""
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "PhishGuard AI"})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Analyze a URL for phishing threats.

    Request Body:
        {"url": "https://example.com"}

    Response:
        {
            "url": "...",
            "prediction": "Phishing" | "Legitimate",
            "confidence": 0.95,
            "features": {...},
            "shap_explanation": "...",
            "shap_plot": "<base64 PNG>",
            "similar_urls": [...]
        }
    """
    try:
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"error": "Missing 'url' field in request body"}), 400

        url = data["url"].strip()
        if not url:
            return jsonify({"error": "URL cannot be empty"}), 400

        # 1. Feature extraction
        features_dict = extract_features(url)
        features_array = extract_features_array(url)
        
        # 1.5 Get NLP Embedding
        url_emb = get_embedding(url)
        full_features = features_array + url_emb

        # 2. ML prediction
        model = get_model()
        features_np = np.array(full_features).reshape(1, -1)
        prediction_proba = model.predict_proba(features_np)[0]
        pred_class = int(model.predict(features_np)[0])
        prediction = "Phishing" if pred_class == 1 else "Legitimate"
        confidence = float(prediction_proba[pred_class])

        # 3. SHAP explanation
        try:
            shap_result = explain(full_features)
            shap_text = get_explanation_text(shap_result)
            shap_contributions = shap_result["feature_contributions"]
        except Exception as e:
            print(f"SHAP error: {e}")
            shap_text = "SHAP explanation unavailable."
            shap_contributions = []

        # 4. RAG - similar URL search
        try:
            similar_urls = rag_search(url, k=5)
        except Exception as e:
            print(f"RAG error: {e}")
            similar_urls = []

        # 5. Build response
        response = {
            "url": url,
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "features": features_dict,
            "shap_explanation": shap_text,
            "shap_contributions": shap_contributions,
            "similar_urls": similar_urls,
        }
        return jsonify(response)

    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


# ── Startup ──────────────────────────────────────────────────────────────────

def init_app():
    """Pre-load model and FAISS index at startup."""
    print("\n" + "=" * 60)
    print("  PhishGuard AI - Starting Server")
    print("=" * 60)
    try:
        get_model()
        print("  [OK] ML Model loaded")
    except Exception as e:
        print(f"  [!!] ML Model: {e}")
    try:
        _load_index()
        print("  [OK] FAISS index loaded")
    except Exception as e:
        print(f"  [!!] FAISS index: {e}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    init_app()
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
