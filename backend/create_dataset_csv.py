import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import os

mp_pose = mp.solutions.pose.Pose()

CSV_FILE = "Training_set.csv"
IMAGE_FOLDER = "train"

data = pd.read_csv(CSV_FILE)

X = []
y = []

for index,row in data.iterrows():

    img_path = os.path.join(
        IMAGE_FOLDER,
        row["filename"]
    )

    label = str(row["label"]).lower()

    # relevant patient activities only
    if "sitting" in label:
        label_id = 0

    elif "sleeping" in label:
        label_id = 1

    elif "running" in label:
        label_id = 2

    elif "dancing" in label or "cycling" in label:
        label_id = 3

    else:
        continue

    img = cv2.imread(img_path)

    if img is None:
        continue

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    result = mp_pose.process(rgb)

    if result.pose_landmarks:

        features = []

        for lm in result.pose_landmarks.landmark:
            features.append(lm.x)
            features.append(lm.y)

        X.append(features)
        y.append(label_id)

np.save("X.npy", X)
np.save("y.npy", y)

print("dataset ready")