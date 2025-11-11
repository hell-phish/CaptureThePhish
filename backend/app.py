from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from predict import predict_text

# --- Initialize FastAPI app ---
app = FastAPI(title="PhishShield API (MVP)", version="1.1")

# --- CORS setup ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # You can restrict this to your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request model ---
class PredictRequest(BaseModel):
    message_id: str | None = None
    subject: str | None = ""
    body: str | None = ""
    from_addr: str | None = None
    to: list | None = None


# --- Health check route ---
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Main prediction endpoint ---
@app.post("/predict")
def predict(req: PredictRequest):
    text = ""

    # Combine subject + body text
    if req.subject:
        text += (req.subject or "") + "\n\n"
    if req.body:
        text += (req.body or "")

    # Run prediction
    res = predict_text(text)

    # --- Return result safely ---
    return {
        "message_id": req.message_id,
        "phish_prob": res.get("phish_prob", 0.0),
        "benign_prob": res.get("benign_prob", 1.0),
        "highlights": res.get("highlights", []),
        "model_version": res.get("model_version", "unknown")
    }
