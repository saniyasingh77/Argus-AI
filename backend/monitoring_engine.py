import cv2
import mediapipe as mp
import time
import winsound

from backend.detection_dl import detect_activity_dl
from backend.database import save_activity
from backend.alert import send_alert


mp_pose = mp.solutions.pose


def run_monitoring():

    # stable camera initialization
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():

        print("Camera not detected")

        return


    cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)


    pose = mp_pose.Pose()

    last_save = 0

    lying_counter = 0

    no_move_counter = 0

    prev_hip_y = None

    last_activity = "Normal"


    # emergency recording
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    emergency_video = cv2.VideoWriter(

        "emergency_recording.avi",

        fourcc,

        20.0,

        (640,480)

    )


    while True:

        ret,frame = cap.read()

        if not ret:

            print("Frame not captured")

            break


        rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        res = pose.process(rgb)


        activity="Normal"

        risk="LOW"


        if res.pose_landmarks:

            mp.solutions.drawing_utils.draw_landmarks(

                frame,

                res.pose_landmarks,

                mp_pose.POSE_CONNECTIONS
            )


            try:

                activity,risk = detect_activity_dl(

                    res.pose_landmarks.landmark
                )

            except Exception as e:

                print("DL error:",e)


            # immobility detection

            hip = res.pose_landmarks.landmark[24]

            if prev_hip_y is not None:

                movement = abs(hip.y-prev_hip_y)

                if movement < 0.002:

                    no_move_counter += 1

                else:

                    no_move_counter = 0


            prev_hip_y = hip.y


            if no_move_counter > 150:

                activity="Immobility detected"

                risk="HIGH"


            # bed exit detection

            if last_activity=="Lying" and activity=="Walking":

                activity="Bed exit detected"

                risk="HIGH"


            last_activity = activity


        # long lying detection

        if activity=="Lying":

            lying_counter += 1

        else:

            lying_counter = 0


        if lying_counter > 200:

            activity="No movement detected"

            risk="HIGH"


        # save activity every 5 sec

        if time.time()-last_save > 5:

            save_activity(activity,risk)

            last_save=time.time()


        # alert system

        if risk=="HIGH":

            print("ALERT:",activity)

            send_alert(activity)

            try:

                winsound.Beep(2500,1000)
            except:
                pass


            emergency_video.write(frame)


        # UI display

        color=(0,255,0)

        if risk=="HIGH":

            color=(0,0,255)

        elif risk=="MEDIUM":

            color=(0,255,255)


        cv2.putText(

            frame,

            activity+" | "+risk,

            (10,40),

            cv2.FONT_HERSHEY_SIMPLEX,

            1,

            color,

            2
        )


        cv2.imshow(

            "Patient Monitoring",

            frame
        )


        if cv2.waitKey(1)==27:

            break


    cap.release()

    emergency_video.release()

    cv2.destroyAllWindows()