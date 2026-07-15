from sklearn.ensemble import RandomForestClassifier
import numpy as np

# 🔥 Training data (improved)
X = [
    [0.15, 0.20, 0.25, 0.55],  # Standing
    [0.05, 0.30, 0.25, 0.65],  # Sitting
    [0.02, 0.02, 0.02, 0.10],  # Lying
    [0.18, 0.22, 0.28, 0.60],  # Walking
]

y = ["Standing", "Sitting", "Lying", "Walking"]

model = RandomForestClassifier(n_estimators=50)
model.fit(X, y)

def predict_activity(features):
    return model.predict([features])[0]