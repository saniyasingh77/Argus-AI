import numpy as np
from tensorflow.keras.models import load_model

model = load_model("backend/activity_model.h5")

labels = [
"Walking",
"Sitting",
"Lying",
"Standing",
"Fall detected"
]

def detect_activity_dl(landmarks):

    features = []

    for lm in landmarks:

        features.append(lm.x)
        features.append(lm.y)

    features = np.array(features)

    pred = model.predict(
        features.reshape(1,-1),
        verbose=0
    )

    idx = np.argmax(pred)

    activity = labels[idx]

    risk = "LOW"

    if activity == "Fall detected":

        risk = "HIGH"

    return activity, risk