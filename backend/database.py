import sqlite3, datetime

from werkzeug.security import generate_password_hash, check_password_hash

from backend.config import DB_PATH, ensure_data_dir, DEMO_USERS


def _connect():
    """Open a connection, guaranteeing the database directory exists."""
    ensure_data_dir()
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create tables up front so read endpoints work on a fresh database."""
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS activity_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity TEXT,
        risk TEXT,
        time TEXT
    )
    """)
    conn.commit()
    conn.close()


def seed_demo_users():
    """Insert known demo accounts if they don't already exist.

    Makes the app usable on ephemeral free hosts where the database resets
    on cold start. Idempotent.
    """
    conn = _connect()
    cur = conn.cursor()
    for name, email, password, role in DEMO_USERS:
        # INSERT OR IGNORE + UNIQUE(email) is race-safe across gunicorn workers.
        cur.execute(
            "INSERT OR IGNORE INTO users(name,email,password,role) VALUES (?,?,?,?)",
            (name, email, generate_password_hash(password), role),
        )
    conn.commit()
    conn.close()


def seed_demo_activity():
    """Populate a realistic activity history so the dashboard looks alive on
    a fresh (ephemeral) database. Idempotent: only seeds an empty log."""
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM activity_log")
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    # activity, risk, minutes-ago
    sample = [
        ("Walking", "LOW", 480),
        ("Sitting", "LOW", 455),
        ("Lying", "MEDIUM", 430),
        ("Sitting", "LOW", 400),
        ("Immobility detected", "HIGH", 360),
        ("Walking", "LOW", 330),
        ("Bed exit detected", "HIGH", 300),
        ("Sitting", "LOW", 260),
        ("Lying", "MEDIUM", 220),
        ("Fall detected", "HIGH", 180),
        ("Walking", "LOW", 150),
        ("Sitting", "LOW", 110),
        ("Emergency gesture", "HIGH", 70),
        ("Lying", "MEDIUM", 40),
        ("Sitting", "LOW", 12),
    ]
    now = datetime.datetime.now()
    for activity, risk, mins in sample:
        ts = now - datetime.timedelta(minutes=mins)
        cur.execute(
            "INSERT INTO activity_log(activity,risk,time) VALUES (?,?,?)",
            (activity, risk, ts.strftime("%Y-%m-%d %H:%M:%S")),
        )
    conn.commit()
    conn.close()


def create_user(name, email, password, role):
    conn = _connect()
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
                (name, email, generate_password_hash(password), role))

    conn.commit()
    conn.close()


def email_exists(email):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE email=?", (email,))
    found = cur.fetchone() is not None
    conn.close()
    return found


def login_user(email, password):
    conn = _connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cur.fetchone()

    conn.close()

    if user is None:
        return None

    stored = user[3]
    # Support both hashed and any legacy plain-text values gracefully.
    try:
        ok = check_password_hash(stored, password)
    except Exception:
        ok = False
    if not ok and stored == password:
        ok = True

    return user if ok else None


def save_activity(activity, risk):
    conn = _connect()
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
