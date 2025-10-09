# backend/predict.py
import os
import re
from typing import Tuple

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

# Try to load joblib model (vectorizer, classifier) saved by Kanak.
def load_model():
    try:
        import joblib
        mdl = joblib.load(MODEL_PATH)
        return mdl
    except Exception as e:
        print("Warning: could not load model.pkl:", e)
        return None

MODEL = load_model()

SUSPICIOUS_WORDS = [
    "verify", "account", "password", "login", "click", "update",
    "bank", "ssn", "urgent", "immediately", "reset", "confirm",
    "billing", "invoice", "suspended", "secure", "verify your account"
]

def heuristic_score(text: str) -> Tuple[float, list]:
    text_lower = text.lower() if text else ""
    count = 0
    highlights = []
    for w in SUSPICIOUS_WORDS:
        for m in re.finditer(re.escape(w), text_lower):
            count += 1
            # map indices to original text if needed (we use lowercased indices)
            highlights.append({"start": m.start(), "end": m.end(), "text": text[m.start():m.end()] if text else w, "label": "suspicious"})
    base = min(0.05 + 0.18 * count, 0.99)
    if re.search(r"https?://", text_lower):
        base = min(base + 0.15, 0.995)
    return base, highlights

def predict_text(text: str):
    """Return dict with phishing_probability, highlights, and model_version."""
    if not text or text.strip() == "":
        return {"phishing_probability": 0.0, "highlights": [], "model_version": "none"}

    # Use sklearn model if available
    if MODEL is not None:
        try:
            # MODEL can be a pipeline/predictor or tuple (vectorizer, clf)
            if hasattr(MODEL, "predict_proba"):
                probs = MODEL.predict_proba([text])[0]
                prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
            else:
                vec, clf = MODEL
                Xv = vec.transform([text])
                probs = clf.predict_proba(Xv)[0]
                prob = float(probs[1])
            # add heuristic highlights for UI clarity
            _, highlights = heuristic_score(text)
            return {"phishing_probability": prob, "highlights": highlights, "model_version": "sklearn-model"}
        except Exception as e:
            # model failed at inference time
            print("Model inference error:", e)

    # fallback heuristic
    prob, highlights = heuristic_score(text)
    return {"phishing_probability": prob, "highlights": highlights, "model_version": "heuristic"}
