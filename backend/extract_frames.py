import cv2
import os

video_folder = "dataset/videos"
output_folder = "dataset/frames"

os.makedirs(output_folder, exist_ok=True)

for video in os.listdir(video_folder):

    path = os.path.join(video_folder, video)

    cap = cv2.VideoCapture(path)

    frame_id = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        if frame_id % 5 == 0:

            name = video.split(".")[0]

            save_path = f"{output_folder}/{name}_{frame_id}.jpg"

            cv2.imwrite(save_path, frame)

        frame_id += 1

    cap.release()