from flask import Flask, request, jsonify, send_from_directory
from backend.monitoring_engine import run_monitoring
from backend.video_processor import process_video
from backend.database import create_user, login_user

import threading
import sqlite3
import pandas as pd
import os
import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FRONTEND_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "frontend")
)

app = Flask(__name__, static_folder=FRONTEND_DIR)



# ================= STATIC FILES =================

@app.route('/static/<path:filename>')
def static_files(filename):

    return send_from_directory(
        FRONTEND_DIR,
        filename
    )



# ================= PAGES =================

@app.route("/")
def login_page():

    return send_from_directory(
        FRONTEND_DIR,
        "login.html"
    )



@app.route("/signup")
def signup_page():

    return send_from_directory(
        FRONTEND_DIR,
        "signup.html"
    )



@app.route("/user")
def user_page():

    return send_from_directory(
        FRONTEND_DIR,
        "user.html"
    )



@app.route("/admin")
def admin_page():

    return send_from_directory(
        FRONTEND_DIR,
        "admin.html"
    )



# ================= AUTH =================

@app.route("/signup", methods=["POST"])
def signup_api():

    data = request.json

    create_user(
        data["name"],
        data["email"],
        data["password"],
        data["role"]
    )

    return jsonify({
        "message":"Signup successful"
    })



@app.route("/login", methods=["POST"])
def login_api():

    data = request.json

    user = login_user(
        data["email"],
        data["password"]
    )

    if user:

        return jsonify({
            "status":"success",
            "role":user[4]
        })

    return jsonify({
        "status":"fail"
    })



# ================= MONITORING =================

@app.route("/start")
def start():

    threading.Thread(
        target=run_monitoring
    ).start()

    return jsonify({
        "message":"Monitoring Started"
    })



@app.route("/video", methods=["POST"])
def video():

    file = request.files["file"]

    file.save("uploaded.mp4")

    threading.Thread(
        target=process_video,
        args=("uploaded.mp4",)
    ).start()

    return jsonify({
        "message":"Video Processing Started"
    })



# ================= REPORT =================

@app.route("/report")
def report():

    try:

        conn = sqlite3.connect("database/patient.db")

        df = pd.read_sql_query(
            "SELECT activity,risk,time FROM activity_log ORDER BY id DESC",
            conn
        )

        conn.close()

        return jsonify(df.to_dict(orient="records"))

    except Exception as e:

        return jsonify({
            "error": str(e)
        }),500
# TODAY SUMMARY (percentage calculation done in frontend)

@app.route("/summary")
def summary():

    today = str(datetime.date.today())

    conn = sqlite3.connect(
        "database/patient.db"
    )

    df = pd.read_sql_query(

        """
        SELECT risk,
        COUNT(*) as count
        FROM activity_log
        WHERE date(time)=?
        GROUP BY risk
        """,

        conn,

        params=[today]
    )

    conn.close()

    return df.to_json(
        orient="records"
    )



# ================= ALERT HISTORY =================

@app.route("/alerts")
def alerts():

    conn = sqlite3.connect(
        "database/patient.db"
    )

    df = pd.read_sql_query(

        """
        SELECT activity,risk,time
        FROM activity_log
        WHERE risk='HIGH'
        ORDER BY id DESC
        """,

        conn
    )

    conn.close()

    return df.to_json(
        orient="records"
    )



# ================= ADMIN =================

@app.route("/get_users")
def get_users():

    conn = sqlite3.connect(
        "database/patient.db"
    )

    cur = conn.cursor()

    cur.execute(
        "SELECT id,name,email,role FROM users"
    )

    users = cur.fetchall()

    conn.close()

    return jsonify(users)



@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):

    conn = sqlite3.connect(
        "database/patient.db"
    )

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM users WHERE id=?",
        (user_id,)
    )

    conn.commit()

    conn.close()

    return jsonify({
        "message":"User deleted successfully"
    })



# ================= RUN =================

if __name__ == "__main__":

    app.run(debug=True)
    