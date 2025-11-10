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


# --- Heuristic Fallback Scoring ---
def heuristic_score(text: str) -> Tuple[float, list]:
    text_lower = text.lower() if text else ""
    count = 0
    highlights = []

    for w in SUSPICIOUS_WORDS:
        for m in re.finditer(re.escape(w), text_lower):
            snippet = text_lower[max(0, m.start() - 20):m.end() + 20]
            # only count word if it appears in suspicious context
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


# --- Predict Function ---
def predict_text(text: str):
    """Return dict with phishing_probability, highlights, and model_version."""
    if not text or text.strip() == "":
        return {"phishing_probability": 0.0, "highlights": [], "model_version": "none"}

    # --- ML Model Prediction ---
    if MODEL is not None:
        try:
            if hasattr(MODEL, "predict_proba"):
                probs = MODEL.predict_proba([text])[0]
                prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
            else:
                # backward compatibility (vectorizer, classifier)
                vec, clf = MODEL
                Xv = vec.transform([text])
                probs = clf.predict_proba(Xv)[0]
                prob = float(probs[1])

            _, highlights = heuristic_score(text)
            return {
                "phishing_probability": prob,
                "highlights": highlights,
                "model_version": "trained-ml"
            }
        except Exception as e:
            print("❌ Model inference error:", e)

    # --- Heuristic Fallback ---
    prob, highlights = heuristic_score(text)
    return {
        "phishing_probability": prob,
        "highlights": highlights,
        "model_version": "heuristic-fallback"
    }
