# backend/train_model.py
import re
import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Path to your Kaggle dataset
CSV_PATH = os.path.join(os.path.dirname(__file__), "phishing_email.csv")

def clean_text(text: str) -> str:
    """Basic text cleanup"""
    text = str(text).lower()
    text = re.sub(r"http\S+", " url ", text)
    text = re.sub(r"\d+", " number ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def load_dataset():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError("❌ Dataset 'emails.csv' not found in backend folder.")
    
    df = pd.read_csv(CSV_PATH)
    if "text_combined" not in df.columns or "label" not in df.columns:
        raise ValueError("❌ Dataset must have 'text_combined' and 'label' columns.")

    df = df.dropna(subset=["text_combined", "label"]).copy()
    df["text_combined"] = df["text_combined"].map(clean_text)
    df = df[df["text_combined"].str.len() > 3].drop_duplicates(subset=["text_combined"])
    
    texts = df["text_combined"].tolist()
    labels = df["label"].astype(int).tolist()
    print(f"📊 Loaded {len(df)} samples (phish={sum(labels)}, benign={len(labels)-sum(labels)})")
    return texts, labels

def main():
    texts, labels = load_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # TF-IDF with unigrams (Step 2 will expand this)
    vectorizer = TfidfVectorizer(max_features=5000)
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf  = vectorizer.transform(X_test)

    # Logistic Regression baseline
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_tfidf, y_train)

    y_pred = model.predict(X_test_tfidf)
    print("\n📈 Evaluation:\n", classification_report(y_test, y_pred, digits=4))

    joblib.dump((vectorizer, model), os.path.join(os.path.dirname(__file__), "model.pkl"))
    print("\n✅ Model saved as backend/model.pkl")

if __name__ == "__main__":
    main()
