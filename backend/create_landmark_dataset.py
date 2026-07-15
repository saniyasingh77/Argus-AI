import cv2
import mediapipe as mp
import numpy as np
import os

mp_pose = mp.solutions.pose.Pose()

X = []
y = []

label_map = {
    "walking":0,
    "sitting":1,
    "lying":2,
    "standing":3,
    "falling":4
}

for label in label_map:

    folder = f"dataset/{label}"

    for img_name in os.listdir(folder):

        img_path = os.path.join(folder,img_name)

        img = cv2.imread(img_path)

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        result = mp_pose.process(rgb)

        if result.pose_landmarks:

            features = []

            for lm in result.pose_landmarks.landmark:

                features.append(lm.x)
                features.append(lm.y)

            X.append(features)
            y.append(label_map[label])

np.save("X.npy", X)
np.save("y.npy", y)