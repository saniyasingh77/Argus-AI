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

def _heuristic_activity(landmarks):
    """Classify the base activity from pose geometry alone (no trained model
    required). Used when the .h5 model is not present so the app still does
    real analysis locally."""
    try:
        shoulder = landmarks[11]
        hip = landmarks[24]
        knee = landmarks[26]
        ankle = landmarks[28]
        # body roughly horizontal -> lying down
        if abs(shoulder.y - ankle.y) < 0.2:
            return "Lying"
        # hip close to knee height -> knees bent -> sitting
        if abs(hip.y - knee.y) < 0.12:
            return "Sitting"
        return "Standing"
    except Exception:
        return "Moving"


def detect_activity_dl(landmarks):

    # convert pose landmarks into feature vector
    features = []

    for lm in landmarks:
        features.append(lm.x)
        features.append(lm.y)

    features = np.array(features)

    # Use the trained model if available; otherwise fall back to pose-geometry
    # heuristics so live monitoring / video analysis still work without the
    # (unshipped) .h5 model file.
    try:
        pred = _get_model().predict(features.reshape(1, -1), verbose=0)
        activity = labels[np.argmax(pred)]
    except Exception:
        activity = _heuristic_activity(landmarks)

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