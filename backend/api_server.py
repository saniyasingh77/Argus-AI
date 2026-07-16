from flask import Flask, request, jsonify, send_from_directory

import threading
import sqlite3
import os
import datetime

from backend.database import (
    create_user,
    login_user,
    init_db,
    seed_demo_users,
    seed_demo_activity,
    email_exists,
    demo_analyze,
)
from backend import config


FRONTEND_DIR = config.FRONTEND_DIR

app = Flask(__name__, static_folder=FRONTEND_DIR)

# Make sure the database directory + tables exist before the first request.
config.ensure_data_dir()
init_db()
if config.SEED_DEMO:
    seed_demo_users()
    seed_demo_activity()


def _query(sql, params=()):
    """Run a read query and return a list of dict rows (no pandas needed)."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ================= STATIC FILES =================

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# ================= HEALTH =================

@app.route("/health")
@app.route("/healthz")
def health():
    """Liveness/readiness probe for Docker & Kubernetes."""
    return jsonify({"status": "ok", "service": "argus-ai"}), 200


# ================= PAGES =================

@app.route("/")
def login_page():
    return send_from_directory(FRONTEND_DIR, "login.html")


@app.route("/signup")
def signup_page():
    return send_from_directory(FRONTEND_DIR, "signup.html")


@app.route("/user")
def user_page():
    return send_from_directory(FRONTEND_DIR, "user.html")


@app.route("/admin")
def admin_page():
    return send_from_directory(FRONTEND_DIR, "admin.html")


# ================= AUTH =================

@app.route("/signup", methods=["POST"])
def signup_api():
    data = request.json or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = data.get("role") or "user"

    if not (name and email and password):
        return jsonify({"status": "fail",
                        "message": "All fields are required"}), 400

    if email_exists(email):
        return jsonify({"status": "fail",
                        "message": "An account with this email already exists"}), 409

    try:
        create_user(name, email, password, role)
    except sqlite3.IntegrityError:
        return jsonify({"status": "fail",
                        "message": "An account with this email already exists"}), 409

    return jsonify({"status": "success", "message": "Account created"})


@app.route("/login", methods=["POST"])
def login_api():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = login_user(email, password)

    if user:
        return jsonify({
            "status": "success",
            "name": user[1],
            "email": user[2],
            "role": user[4],
        })

    return jsonify({"status": "fail", "message": "Invalid email or password"}), 401


# ================= MONITORING =================

def _cv_available():
    """True if the OpenCV + MediaPipe computer-vision stack is installed."""
    try:
        import cv2  # noqa: F401
        import mediapipe  # noqa: F401
        return True
    except Exception:
        return False


@app.route("/start")
def start():
    # If the CV stack is installed (local full install), run the ORIGINAL
    # real-time camera flow. The engine opens the webcam with the reliable
    # DirectShow backend and sends real email / WhatsApp alerts on high risk.
    if _cv_available():
        from backend.monitoring_engine import run_monitoring
        threading.Thread(target=run_monitoring, daemon=True).start()
        return jsonify({
            "mode": "live",
            "message": "Live camera monitoring started — a window opens on this device.",
        })

    # No CV stack (e.g. cloud / Render): demo analysis so the feature still
    # produces visible results in the dashboard.
    detections = demo_analyze(source="live")
    high = sum(1 for d in detections if d["risk"] == "HIGH")
    return jsonify({
        "mode": "demo",
        "message": f"Demo monitoring — {len(detections)} events, {high} alert(s)",
        "detections": detections,
    })


@app.route("/stop")
def stop():
    """Stop a running live-monitoring session (closes the camera window)."""
    try:
        from backend.monitoring_engine import stop_monitoring
        stop_monitoring()
        return jsonify({"message": "Monitoring stopped"})
    except Exception:
        return jsonify({"message": "Monitoring is not running"})


@app.route("/video_status")
def video_status():
    """Report whether a real video analysis is still running, and its results,
    so the dashboard can show them when it finishes."""
    try:
        from backend.video_processor import is_processing, get_last_results
        return jsonify({
            "running": is_processing(),
            "detections": get_last_results(),
        })
    except Exception:
        return jsonify({"running": False, "detections": []})


@app.route("/monitor_status")
def monitor_status():
    """Report whether a live session is still running, so the dashboard can
    reset itself when the user closes the window with X or presses ESC."""
    try:
        from backend.monitoring_engine import is_monitoring
        return jsonify({"running": is_monitoring()})
    except Exception:
        return jsonify({"running": False})


@app.route("/video", methods=["POST"])
def video():
    file = request.files.get("file")
    if file is None or not file.filename:
        return jsonify({"message": "No video file was uploaded"}), 400

    # If the CV stack is installed (local full install), run the ORIGINAL
    # frame-by-frame analysis — it opens an analysis window on that device.
    if _cv_available():
        from backend.video_processor import process_video
        config.ensure_data_dir()
        upload_path = os.path.join(config.DATA_DIR, "uploaded.mp4")
        file.save(upload_path)
        threading.Thread(target=process_video, args=(upload_path,), daemon=True).start()
        return jsonify({
            "mode": "live",
            "message": "Video analysis started — results appear in Reports.",
        })

    # No CV stack (e.g. cloud / Render): demo analysis with visible results.
    detections = demo_analyze(source="video", name=file.filename)
    high = sum(1 for d in detections if d["risk"] == "HIGH")
    return jsonify({
        "mode": "demo",
        "message": f"Demo analysis — {len(detections)} activities, {high} alert(s)",
        "detections": detections,
    })


# ================= REPORT =================

@app.route("/report")
def report():
    try:
        rows = _query(
            "SELECT activity,risk,time FROM activity_log ORDER BY id DESC"
        )
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# TODAY SUMMARY (percentage calculation done in frontend)

@app.route("/summary")
def summary():
    today = str(datetime.date.today())
    rows = _query(
        """
        SELECT risk, COUNT(*) as count
        FROM activity_log
        WHERE date(time)=?
        GROUP BY risk
        """,
        (today,),
    )
    return jsonify(rows)


# ================= ALERT HISTORY =================

@app.route("/alerts")
def alerts():
    rows = _query(
        """
        SELECT activity,risk,time
        FROM activity_log
        WHERE risk='HIGH'
        ORDER BY id DESC
        """
    )
    return jsonify(rows)


# ================= DASHBOARD STATS =================

@app.route("/stats")
def stats():
    """Aggregate counts for the dashboard tiles and risk chart."""
    by_risk = {r["risk"]: r["count"] for r in _query(
        "SELECT risk, COUNT(*) as count FROM activity_log GROUP BY risk"
    )}
    total = sum(by_risk.values())
    users = _query("SELECT COUNT(*) as c FROM users")[0]["c"]
    last = _query(
        "SELECT activity, risk, time FROM activity_log ORDER BY id DESC LIMIT 1"
    )
    return jsonify({
        "total_events": total,
        "high": by_risk.get("HIGH", 0),
        "medium": by_risk.get("MEDIUM", 0),
        "low": by_risk.get("LOW", 0),
        "users": users,
        "latest": last[0] if last else None,
    })


# ================= ADMIN =================

@app.route("/get_users")
def get_users():
    conn = sqlite3.connect(config.DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id,name,email,role FROM users")
    users = cur.fetchall()
    conn.close()
    return jsonify(users)


@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    conn = sqlite3.connect(config.DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User deleted successfully"})


# ================= RUN =================

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
