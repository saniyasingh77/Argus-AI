import sqlite3, datetime

def create_user(name, email, password, role):
    conn = sqlite3.connect("database/patient.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("INSERT INTO users(name,email,password,role) VALUES (?,?,?,?)",
                (name, email, password, role))

    conn.commit()
    conn.close()


def login_user(email, password):
    conn = sqlite3.connect("database/patient.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cur.fetchone()

    conn.close()
    return user


def save_activity(activity, risk):
    conn = sqlite3.connect("database/patient.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS activity_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity TEXT,
        risk TEXT,
        time TEXT
    )
    """)

    cur.execute("INSERT INTO activity_log(activity,risk,time) VALUES (?,?,?)",
                (activity, risk, str(datetime.datetime.now())))

    conn.commit()
    conn.close()