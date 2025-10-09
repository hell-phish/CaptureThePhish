# backend/train_model.py

import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Some example emails
data = [
    ("Please verify your account by clicking this link", 1),
    ("Your invoice is attached", 0),
    ("Reset your password immediately: http://phish.com", 1),
    ("Monthly newsletter from your bank", 0),
    ("Confirm your payment info", 1),
    ("Meeting tomorrow at 10am", 0)
]

# Split into text and labels
texts = [d[0] for d in data]
labels = [d[1] for d in data]

# Clean text (remove extra spaces)
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    return text

texts = [clean_text(t) for t in texts]

# Split data into training and testing
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.3, random_state=42)

# Convert text to numeric features (TF-IDF)
vectorizer = TfidfVectorizer(max_features=1000)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train a Logistic Regression model
model = LogisticRegression()
model.fit(X_train_tfidf, y_train)

# Evaluate it
y_pred = model.predict(X_test_tfidf)
print("Evaluation:")
print(classification_report(y_test, y_pred))

# Save the model to a file (model.pkl)
joblib.dump((vectorizer, model), "model.pkl")
print("✅ Model saved as model.pkl in the backend folder!")
