/**
 * PhishGuard AI - Frontend Logic
 * ================================
 * Handles form submission, API calls, and dynamic result rendering.
 */

const API_URL = "/api/analyze";

// ── DOM Elements ────────────────────────────────────────────────────────────
const form = document.getElementById("searchForm");
const urlInput = document.getElementById("urlInput");
const submitBtn = document.getElementById("submitBtn");
const resultsSection = document.getElementById("results");
const toastEl = document.getElementById("toast");

// ── Form Submit ─────────────────────────────────────────────────────────────
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const url = urlInput.value.trim();
    if (!url) return;

    setLoading(true);
    hideResults();
    
    // Trigger Hero Transition
    document.getElementById("heroSection").classList.add("hero-section--active");

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || `Server error (${res.status})`);
        }

        const data = await res.json();
        renderResults(data);
    } catch (err) {
        showToast(err.message || "Analysis failed. Please try again.");
    } finally {
        setLoading(false);
    }
});

// ── Loading State ───────────────────────────────────────────────────────────
function setLoading(loading) {
    submitBtn.disabled = loading;
    if (loading) {
        submitBtn.classList.add("search-btn--loading");
    } else {
        submitBtn.classList.remove("search-btn--loading");
    }
}

// ── Render Results ──────────────────────────────────────────────────────────
function renderResults(data) {
    const isPhishing = data.prediction === "Phishing";
    const confidence = (data.confidence * 100).toFixed(1);

    // Verdict banner
    const verdictEl = document.getElementById("verdict");
    verdictEl.className = `verdict ${isPhishing ? "verdict--phishing" : "verdict--safe"}`;
    document.getElementById("verdictIcon").textContent = isPhishing ? "⚠️" : "✅";
    document.getElementById("verdictLabel").textContent = isPhishing ? "Phishing Detected" : "URL is Safe";
    document.getElementById("verdictConfidence").textContent = `Analyzed: ${data.url}`;
    document.getElementById("verdictScoreValue").textContent = `${confidence}%`;
    verdictEl.querySelector(".verdict__score-value").className =
        `verdict__score-value`;


    // Feature contributions
    renderContributions(data.shap_contributions || []);

    // Similar URLs
    renderSimilarUrls(data.similar_urls || []);

    // Show results
    resultsSection.classList.add("results--visible");
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── Feature Contributions ───────────────────────────────────────────────────
function renderContributions(contributions) {
    const list = document.getElementById("contribList");
    list.innerHTML = "";

    const top = contributions.slice(0, 10);
    if (top.length === 0) {
        list.innerHTML = '<li class="contrib-item"><span class="contrib-name">No data available</span></li>';
        return;
    }

    const maxAbs = Math.max(...top.map(c => Math.abs(c.shap_value)), 0.001);

    top.forEach((c) => {
        const isPositive = c.shap_value > 0;
        const barWidth = Math.min((Math.abs(c.shap_value) / maxAbs) * 100, 100);
        const name = c.feature.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());

        const li = document.createElement("li");
        li.className = "contrib-item";
        li.innerHTML = `
            <span class="contrib-name">${name}</span>
            <span class="contrib-value">${c.value}</span>
            <div class="contrib-bar-wrap">
                <div class="contrib-bar ${isPositive ? "contrib-bar--positive" : "contrib-bar--negative"}"
                     style="width: ${barWidth}%"></div>
            </div>
            <span class="contrib-impact ${isPositive ? "contrib-impact--positive" : "contrib-impact--negative"}">
                ${c.shap_value > 0 ? "+" : ""}${c.shap_value.toFixed(4)}
            </span>
        `;
        list.appendChild(li);
    });
}

// ── Similar URLs ────────────────────────────────────────────────────────────
function renderSimilarUrls(urls) {
    const list = document.getElementById("similarList");
    list.innerHTML = "";

    if (urls.length === 0) {
        list.innerHTML = `
            <li class="similar-item">
                <span class="similar-url" style="color: var(--text-muted)">No similar phishing URLs found</span>
            </li>`;
        return;
    }

    urls.forEach((item) => {
        const score = (item.similarity_score * 100).toFixed(1);
        const li = document.createElement("li");
        li.className = "similar-item";
        li.innerHTML = `
            <div class="similar-icon">🔗</div>
            <span class="similar-url" title="${item.url}">${item.url}</span>
            <span class="similar-score">${score}%</span>
        `;
        list.appendChild(li);
    });
}

// ── Helpers ─────────────────────────────────────────────────────────────────
function hideResults() {
    resultsSection.classList.remove("results--visible");
}

let toastTimer;
function showToast(message) {
    toastEl.textContent = message;
    toastEl.classList.add("toast--visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("toast--visible"), 5000);
}

// ── 3D Card Hover & Tilt Effects ─────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    // We bind tilt events dynamically to elements with .card or .verdict classes
    document.addEventListener("mousemove", (e) => {
        const tiltElements = document.querySelectorAll(".card, .verdict, .search-card");
        
        tiltElements.forEach(card => {
            const rect = card.getBoundingClientRect();
            // Check if mouse is over the card
            if (e.clientX >= rect.left && e.clientX <= rect.right &&
                e.clientY >= rect.top && e.clientY <= rect.bottom) {
                
                // Calculate rotation (max 10 degrees)
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = ((y - centerY) / centerY) * -10;
                const rotateY = ((x - centerX) / centerX) * 10;
                
                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
                card.style.boxShadow = `0 20px 40px rgba(0,0,0,0.4), inset 0 0 0 1px rgba(255,255,255,0.1)`;
            } else {
                // Reset card if mouse leaves
                card.style.transform = `perspective(1000px) rotateX(0) rotateY(0) translateY(0)`;
                card.style.boxShadow = `0 10px 30px rgba(0,0,0,0.3)`;
            }
        });
    });
});

