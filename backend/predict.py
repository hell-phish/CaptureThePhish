import os
import re
import joblib
from typing import Tuple

# --- Paths ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

# --- Suspicious indicators for heuristic fallback ---
SUSPICIOUS_WORDS = [
    "verify", "account", "password", "login", "click", "update",
    "bank", "ssn", "urgent", "immediately", "reset", "confirm",
    "billing", "invoice", "suspended", "secure", "verify your account"
]

# --- Text cleaning (consistent with training preprocessing) ---
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)          # remove URLs
    text = re.sub(r"[^a-z0-9\s]", " ", text)      # remove special chars
    text = re.sub(r"\s+", " ", text).strip()      # normalize spaces
    return text


# --- Load ML model ---
def load_model():
    try:
        model = joblib.load(MODEL_PATH)
        print(f"✅ Model loaded successfully from: {MODEL_PATH}")
        return model
    except Exception as e:
        print(f"⚠️ Warning: could not load model.pkl ({e}) — using heuristic fallback.")
        return None


MODEL = load_model()


# --- Heuristic fallback scoring ---
def heuristic_score(text: str) -> Tuple[float, list]:
    text_lower = text.lower() if text else ""
    count = 0
    highlights = []

    for w in SUSPICIOUS_WORDS:
        for m in re.finditer(re.escape(w), text_lower):
            snippet = text_lower[max(0, m.start() - 20):m.end() + 20]
            if any(x in snippet for x in ["click", "link", "http", "urgent", "verify", "password"]):
                count += 1
                highlights.append({
                    "start": m.start(),
                    "end": m.end(),
                    "text": text[m.start():m.end()],
                    "label": "suspicious"
                })

    base = min(0.02 + 0.1 * count, 0.9)
    if re.search(r"https?://", text_lower):
        base = min(base + 0.1, 0.95)
    if count == 0:
        base = 0.05  # neutral baseline for safe emails

    return base, highlights


# --- Main prediction function ---
def predict_text(text: str):
    """Return dict with phishing probability, highlights, and model version."""
    if not text or text.strip() == "":
        return {
            "phish_prob": 0.0,
            "benign_prob": 1.0,
            "highlights": [],
            "model_version": "none"
        }

    # Clean text before inference
    text_clean = clean_text(text)

    # Short-input guard (1–2 words → too little context)
    if len(text_clean.split()) < 3:
        return {
            "phish_prob": 0.02,
            "benign_prob": 0.98,
            "highlights": [],
            "model_version": "short-input-guard"
        }

    # --- ML model prediction ---
    if MODEL is not None:
        try:
            if hasattr(MODEL, "predict_proba"):
                probs = MODEL.predict_proba([text_clean])[0]
                phish_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
            else:
                # backward compatibility for (vectorizer, classifier)
                vec, clf = MODEL
                Xv = vec.transform([text_clean])
                probs = clf.predict_proba(Xv)[0]
                phish_prob = float(probs[1])

            _, highlights = heuristic_score(text_clean)
            return {
                "phish_prob": round(phish_prob, 3),
                "benign_prob": round(1 - phish_prob, 3),
                "highlights": highlights,
                "model_version": "trained-ml"
            }
        except Exception as e:
            print("❌ Model inference error:", e)

    # --- Heuristic fallback if model missing or fails ---
    prob, highlights = heuristic_score(text_clean)
    return {
        "phish_prob": round(prob, 3),
        "benign_prob": round(1 - prob, 3),
        "highlights": highlights,
        "model_version": "heuristic-fallback"
    }
