import cv2
import mediapipe as mp
import datetime
import time
import threading

from backend.detection_dl import detect_activity_dl
from backend.database import save_activity
from backend.alert import send_alert


mp_pose = mp.solutions.pose

WINDOW_NAME = "Video Analysis"

# Minimum seconds between alerts, so a sustained high-risk pose doesn't fire an
# email/WhatsApp on every frame (which would stall playback and spam messages).
ALERT_COOLDOWN_SEC = 30

# Only record a detection this often. Saving on every frame would write ~30
# rows per second and flood the activity log.
SAVE_EVERY_SEC = 1.0

_processing = threading.Event()
_last_results = []


def is_processing():
    """True while a video is being analysed."""
    return _processing.is_set()


def get_last_results():
    """Detections from the most recent analysis (for the dashboard)."""
    return list(_last_results)


def process_video(path):
    """Public entry point: always clears the processing flag when done."""
    global _last_results
    _processing.set()
    _last_results = []
    try:
        _last_results = _process_video(path)
    except Exception as e:
        print("Video analysis error:", e)
    finally:
        _processing.clear()


def _process_video(path):

    results = []
    last_alert = 0
    last_save = 0

    cap = cv2.VideoCapture(path)

    if not cap.isOpened():
        print("Could not open video:", path)
        return results

    # A fresh Pose per run — the mediapipe object is not thread-safe and may be
    # used at the same time as live monitoring.
    pose = mp_pose.Pose()

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)

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
                mp_pose.POSE_CONNECTIONS,
            )

            try:
                activity, risk = detect_activity_dl(res.pose_landmarks.landmark)
            except Exception as e:
                print("Detection error:", e)

            now = time.time()

            # Throttled save (see SAVE_EVERY_SEC)
            if now - last_save > SAVE_EVERY_SEC:
                last_save = now
                save_activity(activity, risk)
                results.append({
                    "activity": activity,
                    "risk": risk,
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })

            # Rate-limited, non-blocking alert (see ALERT_COOLDOWN_SEC)
            if risk == "HIGH" and now - last_alert > ALERT_COOLDOWN_SEC:
                last_alert = now
                threading.Thread(
                    target=send_alert, args=(activity,), daemon=True
                ).start()

        color = (0, 255, 0)
        if risk == "HIGH":
            color = (0, 0, 255)
        elif risk == "MEDIUM":
            color = (0, 255, 255)

        cv2.putText(
            frame,
            activity + " | " + risk,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2,
        )

        cv2.imshow(WINDOW_NAME, frame)

        # Exit on 'q' or ESC
        key = cv2.waitKey(25) & 0xFF
        if key == ord("q") or key == 27:
            break

        # Exit when the window is closed with the X button
        try:
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break
        except Exception:
            break

    cap.release()
    pose.close()
    cv2.destroyAllWindows()
    for _ in range(4):
        cv2.waitKey(1)

    return results
