import cv2
import mediapipe as mp

from backend.detection_dl import detect_activity_dl
from backend.database import save_activity
from backend.alert import send_alert


mp_pose = mp.solutions.pose
pose = mp_pose.Pose()


def process_video(path):

    cap = cv2.VideoCapture(path)

    while True:

        ret, frame = cap.read()

        if not ret:
            break


        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        res = pose.process(rgb)


        activity = "Normal"
        risk = "LOW"


        if res.pose_landmarks:

            mp.solutions.drawing_utils.draw_landmarks(

                frame,

                res.pose_landmarks,

                mp_pose.POSE_CONNECTIONS
            )


            activity, risk = detect_activity_dl(

                res.pose_landmarks.landmark
            )


            save_activity(activity, risk)


            if risk == "HIGH":

                send_alert(activity)


        color = (0,255,0)

        if risk == "HIGH":

            color = (0,0,255)


        cv2.putText(

            frame,

            activity + " | " + risk,

            (20,40),

            cv2.FONT_HERSHEY_SIMPLEX,

            1,

            color,

            2
        )


        cv2.imshow(

            "Video Analysis",

            frame
        )


        if cv2.waitKey(25) & 0xFF == ord("q"):

            break


    cap.release()

    cv2.destroyAllWindows()