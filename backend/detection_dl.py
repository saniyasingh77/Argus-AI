import numpy as np
from tensorflow.keras.models import load_model

# load trained deep learning model
model = load_model("backend/activity_model.h5")

# output classes
labels = [
    "Sitting",
    "Lying",
    "Walking",
    "Moving"
]

def detect_activity_dl(landmarks):

    # convert pose landmarks into feature vector
    features = []

    for lm in landmarks:
        features.append(lm.x)
        features.append(lm.y)

    features = np.array(features)

    # deep learning prediction
    pred = model.predict(
        features.reshape(1,-1),
        verbose=0
    )

    activity = labels[np.argmax(pred)]

    risk = "LOW"

    # ---------------- FALL DETECTION ----------------

    shoulder = landmarks[11]
    hip = landmarks[24]
    ankle = landmarks[28]

    # body horizontal → fall
    body_horizontal = abs(shoulder.y - ankle.y) < 0.15

    if body_horizontal:
        activity = "Fall detected"
        risk = "HIGH"

    # ---------------- EMERGENCY HAND SIGNAL ----------------

    wrist = landmarks[16]
    shoulder = landmarks[12]

    # hand above shoulder → help gesture
    if wrist.y < shoulder.y:
        activity = "Emergency gesture"
        risk = "HIGH"

    # ---------------- RISK LEVEL ----------------

    if activity == "Lying":
        risk = "MEDIUM"

    return activity, risk