# backend/app.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from predict import predict_text

app = FastAPI(title="PhishShield API (MVP)")

# CORS for local dev and Vercel demo. For production, restrict origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    message_id: str | None = None
    subject: str | None = ""
    body: str | None = ""
    from_addr: str | None = None
    to: list | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(req: PredictRequest):
    text = ""
    if req.subject:
        text += (req.subject or "") + "\n\n"
    if req.body:
        text += (req.body or "")
    res = predict_text(text)
    return {
        "message_id": req.message_id,
        "phish_prob": round(res["phishing_probability"], 4),
        "benign_prob": round(1 - res["phishing_probability"], 4),
        "highlights": res.get("highlights", []),
        "model_version": res.get("model_version", "unknown")
    }
