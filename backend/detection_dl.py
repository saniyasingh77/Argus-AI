import os
import numpy as np

from backend.config import MODEL_PATH

# output classes
labels = [
    "Sitting",
    "Lying",
    "Walking",
    "Moving"
]

# The trained model is loaded lazily on first prediction so that importing
# this module never crashes when the .h5 file is absent (e.g. in CI or a
# freshly-built container before the model artifact is mounted).
_model = None


def _get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Activity model not found at {MODEL_PATH}. "
                "Train it with `python -m backend.train_dl_model` or mount "
                "the artifact via ARGUS_MODEL_PATH."
            )
        from tensorflow.keras.models import load_model
        _model = load_model(MODEL_PATH)
    return _model

def detect_activity_dl(landmarks):

    # convert pose landmarks into feature vector
    features = []

    for lm in landmarks:
        features.append(lm.x)
        features.append(lm.y)

    features = np.array(features)

    # deep learning prediction
    pred = _get_model().predict(
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