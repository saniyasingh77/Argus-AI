import cv2
import mediapipe as mp
import time
import threading

try:
    import winsound  # Windows-only; alert beep is best-effort
except ImportError:  # pragma: no cover - non-Windows / headless
    winsound = None

from backend.detection_dl import detect_activity_dl
from backend.database import save_activity
from backend.alert import send_alert


mp_pose = mp.solutions.pose

WINDOW_NAME = "Patient Monitoring"

# Minimum seconds between two alerts, so a sustained high-risk pose does not
# fire an email/WhatsApp on every frame.
ALERT_COOLDOWN_SEC = 30

# Set by stop_monitoring() (e.g. the dashboard's Stop button) to end the loop.
_stop_event = threading.Event()

# Set while a monitoring session is actually running, so the dashboard can tell
# when the session ended (ESC / X button / Stop) and update itself.
_running = threading.Event()


def is_monitoring():
    """True while a live monitoring session is running."""
    return _running.is_set()


def _beep():
    """Short, non-blocking alert beep (best-effort, Windows only)."""
    if winsound is None:
        return
    try:
        winsound.Beep(2500, 400)
    except Exception:
        pass


def stop_monitoring():
    """Ask a running monitoring loop to shut down and close its window."""
    _stop_event.set()


def _window_closed():
    """True once the user closes the window with the X button."""
    try:
        return cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1
    except Exception:
        return True


def run_monitoring():
    """Public entry point. Always clears the running flag when the session
    ends — however it ends (ESC, X button, Stop button, or an error)."""
    try:
        _run_monitoring()
    except Exception as e:
        print("Monitoring error:", e)
    finally:
        _running.clear()
        _stop_event.clear()


def _run_monitoring():

    _stop_event.clear()

    # stable camera initialization
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():

        print("Camera not detected")

        return


    _running.set()

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)


    pose = mp_pose.Pose()

    last_save = 0

    last_alert = 0

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


    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)

    while True:

        # Stop requested from the dashboard (/stop)
        if _stop_event.is_set():
            break

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
        # Alerts are rate-limited and sent on a background thread: sending an
        # email + WhatsApp (or beeping) on every frame would block the capture
        # loop and freeze the video, and would spam hundreds of messages.

        if risk=="HIGH":

            if time.time() - last_alert > ALERT_COOLDOWN_SEC:

                last_alert = time.time()

                print("ALERT:", activity)

                threading.Thread(
                    target=send_alert, args=(activity,), daemon=True
                ).start()

                threading.Thread(target=_beep, daemon=True).start()


            emergency_video.write(frame)


        # UI display

        color=(0,255,0)

        if risk=="HIGH":

            color=(0,0,255)

        elif risk=="MEDIUM":

            color=(0,255,255)


        h, w = frame.shape[:2]

        # Bottom status bar (always visible)
        cv2.rectangle(frame, (0, h - 44), (w, h), (0, 0, 0), -1)
        cv2.putText(
            frame, f"{activity}  |  RISK: {risk}", (16, h - 14),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2,
        )
        cv2.putText(
            frame, "Argus AI Live  -  press ESC or close window to stop",
            (16, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1,
        )

        # Prominent red ALERT banner on high risk
        if risk == "HIGH":
            cv2.rectangle(frame, (0, 40), (w, 84), (0, 0, 200), -1)
            cv2.putText(
                frame, f"!! ALERT: {activity} !!", (16, 72),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2,
            )


        cv2.imshow(WINDOW_NAME, frame)


        # Exit on ESC or 'q'
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break

        # Exit when the window is closed with the X button
        if _window_closed():
            break


    cap.release()

    emergency_video.release()

    cv2.destroyAllWindows()
    # Extra waitKey ticks let OpenCV actually tear the window down on Windows.
    for _ in range(4):
        cv2.waitKey(1)