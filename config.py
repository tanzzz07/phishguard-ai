"""
PhishGuard AI - Central Configuration
======================================
All paths, model parameters, and API settings in one place.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "model")
RAG_DIR = os.path.join(BASE_DIR, "rag")
STATIC_DIR = os.path.join(BASE_DIR, "static")

DATASET_PATH = os.path.join(DATA_DIR, "phishing_embeddings_100k.csv")
MODEL_PATH = os.path.join(MODEL_DIR, "xgb_model.pkl")
FAISS_INDEX_PATH = os.path.join(RAG_DIR, "faiss_index.bin")
FAISS_URLS_PATH = os.path.join(RAG_DIR, "indexed_urls.pkl")

# ── Model Hyperparameters ────────────────────────────────────────────────────
XGB_PARAMS = {
    "max_depth": 8,
    "n_estimators": 250,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "random_state": 42,
    "n_jobs": -1
}

# ── Feature Configuration ────────────────────────────────────────────────────
LEXICAL_FEATURE_NAMES = [
    "url_length",
    "num_dots",
    "num_hyphens",
    "num_underscores",
    "num_slashes",
    "num_question_marks",
    "num_at_symbols",
    "num_ampersands",
    "num_digits",
    "has_https",
    "has_ip_address",
    "num_subdomains",
    "path_length",
    "domain_length",
    "has_suspicious_keywords",
    "domain_entropy",
    "is_high_risk_tld",
    "vowel_consonant_ratio",
]

# Total features = 18 lexical + 384 embeddings = 402
FEATURE_NAMES = LEXICAL_FEATURE_NAMES + [f"emb_{i}" for i in range(384)]

SUSPICIOUS_KEYWORDS = [
    "login", "signin", "verify", "update", "secure", "account",
    "bank", "confirm", "password", "suspend", "alert", "urgent",
    "expire", "unlock", "validate", "authenticate", "billing",
]

# ── RAG Configuration ────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
RAG_TOP_K = 5  # Number of similar URLs to retrieve

# ── LLM Configuration ────────────────────────────────────────────────────────
# Gemini API removed per user request

# ── Flask Configuration ──────────────────────────────────────────────────────
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True
