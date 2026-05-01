"""
PhishGuard AI - Feature Extraction Module
==========================================
Extracts 15 engineered features from a URL string for phishing detection.

Features:
    1.  url_length          — Total character count of the URL
    2.  num_dots            — Count of '.' characters
    3.  num_hyphens         — Count of '-' characters
    4.  num_underscores     — Count of '_' characters
    5.  num_slashes         — Count of '/' characters
    6.  num_question_marks  — Count of '?' characters
    7.  num_at_symbols      — Count of '@' characters
    8.  num_ampersands      — Count of '&' characters
    9.  num_digits          — Count of digit characters
    10. has_https           — Whether URL uses HTTPS (1/0)
    11. has_ip_address      — Whether domain is an IP address (1/0)
    12. num_subdomains      — Number of subdomains
    13. path_length         — Length of the URL path component
    14. domain_length       — Length of the domain name
    15. has_suspicious_keywords — Whether URL contains phishing keywords (1/0)
"""

import re
import math
from collections import Counter
from urllib.parse import urlparse

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LEXICAL_FEATURE_NAMES, FEATURE_NAMES, SUSPICIOUS_KEYWORDS


def extract_features(url: str) -> dict:
    """
    Extract all 15 features from a URL string.

    Args:
        url: The URL string to analyze.

    Returns:
        A dictionary mapping feature names to their computed values.
    """
    # Ensure the URL has a scheme for proper parsing
    parsed_url = url
    if not url.startswith(("http://", "https://")):
        parsed_url = "http://" + url

    try:
        parsed = urlparse(parsed_url)
    except Exception:
        parsed = urlparse("http://invalid.com")

    domain = parsed.netloc or ""
    path = parsed.path or ""
    url_lower = url.lower()

    features = {
        "url_length": len(url),
        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_underscores": url.count("_"),
        "num_slashes": url.count("/"),
        "num_question_marks": url.count("?"),
        "num_at_symbols": url.count("@"),
        "num_ampersands": url.count("&"),
        "num_digits": sum(c.isdigit() for c in url),
        "has_https": 1 if url.lower().startswith("https") else 0,
        "has_ip_address": 1 if _is_ip_address(domain) else 0,
        "num_subdomains": _count_subdomains(domain),
        "path_length": len(path),
        "domain_length": len(domain),
        "has_suspicious_keywords": 1 if _has_suspicious_keywords(url_lower) else 0,
        "domain_entropy": _calculate_entropy(domain),
        "is_high_risk_tld": 1 if _is_high_risk_tld(domain) else 0,
        "vowel_consonant_ratio": _vowel_consonant_ratio(domain),
    }

    return features


def extract_features_array(url: str) -> list:
    """
    Extract features as an ordered list matching FEATURE_NAMES from config.

    Args:
        url: The URL string to analyze.

    Returns:
        A list of feature values in the order defined by FEATURE_NAMES.
    """
    features = extract_features(url)
    return [features[name] for name in LEXICAL_FEATURE_NAMES]


def _is_ip_address(domain: str) -> bool:
    """Check if the domain is an IP address (IPv4)."""
    # Remove port if present
    host = domain.split(":")[0]
    # IPv4 pattern
    ipv4_pattern = re.compile(
        r"^(\d{1,3}\.){3}\d{1,3}$"
    )
    return bool(ipv4_pattern.match(host))


def _count_subdomains(domain: str) -> int:
    """Count the number of subdomains in the domain."""
    # Remove port if present
    host = domain.split(":")[0]
    parts = host.split(".")
    # domain.tld = 0 subdomains, sub.domain.tld = 1, etc.
    if len(parts) <= 2:
        return 0
    return len(parts) - 2


def _has_suspicious_keywords(url_lower: str) -> bool:
    """Check if the URL contains any suspicious phishing keywords."""
    return any(keyword in url_lower for keyword in SUSPICIOUS_KEYWORDS)


def _calculate_entropy(text: str) -> float:
    """Calculate the Shannon entropy of a string."""
    if not text:
        return 0.0
    entropy = 0.0
    length = len(text)
    counts = Counter(text)
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return float(entropy)


def _is_high_risk_tld(domain: str) -> bool:
    """Check if domain uses a high-risk TLD."""
    high_risk_tlds = {'.xyz', '.top', '.tk', '.ml', '.ga', '.cf', '.gq', '.cc', '.buzz', '.icu'}
    host = domain.split(":")[0]
    parts = host.split(".")
    if len(parts) > 1:
        tld = "." + parts[-1].lower()
        return tld in high_risk_tlds
    return False


def _vowel_consonant_ratio(domain: str) -> float:
    """Calculate the ratio of vowels to consonants in the domain name."""
    host = domain.split(":")[0].lower()
    vowels = set("aeiou")
    consonants = set("bcdfghjklmnpqrstvwxyz")
    v_count = sum(1 for char in host if char in vowels)
    c_count = sum(1 for char in host if char in consonants)
    if c_count == 0:
        return float(v_count)
    return float(v_count / c_count)


# ── Quick Test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_urls = [
        "https://www.google.com",
        "http://192.168.1.1/login/secure-bank/verify?user=admin",
        "https://secure-login.bank-verify.com/account/update",
        "https://github.com/user/repo",
        "http://phishing-site.xyz/confirm-password&redirect=evil.com",
    ]

    print("=" * 80)
    print("PhishGuard AI — Feature Extraction Test")
    print("=" * 80)

    for url in test_urls:
        features = extract_features(url)
        print(f"\nURL: {url}")
        for name, value in features.items():
            print(f"  {name:30s} = {value}")
        print("-" * 60)
