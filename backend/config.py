"""
Central configuration for Argus AI.

All paths and secrets are resolved here so the app behaves identically
whether it is started from the repo root, from a systemd unit, or from
inside a Docker container (where the working directory may differ).

Values are read from environment variables (see .env.example) with safe
defaults for local development.
"""

import os

# Load a local .env file if python-dotenv is available. This is optional:
# in production (Docker/Kubernetes) real environment variables are injected
# by the platform and no .env file is present.
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional at runtime
    pass


# --- Filesystem layout -------------------------------------------------------

# backend/  ->  repo root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

FRONTEND_DIR = os.path.abspath(os.path.join(ROOT_DIR, "frontend"))

# Where the SQLite database lives. Absolute + configurable so it works
# regardless of the process working directory, and so a container can mount
# it on a persistent volume.
# SQLite location. Absolute + env-configurable so it works regardless of the
# process working directory, and so a container can mount it on a volume.
DATA_DIR = os.environ.get("ARGUS_DATA_DIR", os.path.join(ROOT_DIR, "database"))
DB_PATH = os.environ.get("ARGUS_DB_PATH", os.path.join(DATA_DIR, "patient.db"))

# Seed known demo logins (demo@argus.ai / admin@argus.ai) + sample activity on
# startup so the app is immediately usable and the dashboard is populated.
# ON by default; set ARGUS_SEED_DEMO=false to disable in a real deployment.
SEED_DEMO = os.environ.get("ARGUS_SEED_DEMO", "true").lower() in ("1", "true", "yes")
DEMO_USERS = [
    ("Demo User", "demo@argus.ai", "demo123", "user"),
    ("Demo Admin", "admin@argus.ai", "admin123", "admin"),
]

# Trained deep-learning model (optional; the web tier runs without it).
MODEL_PATH = os.environ.get(
    "ARGUS_MODEL_PATH", os.path.join(BASE_DIR, "activity_model.h5")
)


# --- Server ------------------------------------------------------------------

HOST = os.environ.get("ARGUS_HOST", "0.0.0.0")
PORT = int(os.environ.get("ARGUS_PORT", "5000"))
DEBUG = os.environ.get("ARGUS_DEBUG", "false").lower() in ("1", "true", "yes")


# --- Alerting secrets (never hard-code these) --------------------------------

# Email
SMTP_HOST = os.environ.get("ARGUS_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("ARGUS_SMTP_PORT", "465"))
ALERT_EMAIL_SENDER = os.environ.get("ARGUS_EMAIL_SENDER", "")
ALERT_EMAIL_PASSWORD = os.environ.get("ARGUS_EMAIL_PASSWORD", "")
ALERT_EMAIL_RECIPIENTS = [
    e.strip()
    for e in os.environ.get("ARGUS_EMAIL_RECIPIENTS", "").split(",")
    if e.strip()
]

# Twilio / WhatsApp
TWILIO_ACCOUNT_SID = os.environ.get("ARGUS_TWILIO_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("ARGUS_TWILIO_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.environ.get("ARGUS_WHATSAPP_FROM", "whatsapp:+14155238886")
TWILIO_WHATSAPP_TO = os.environ.get("ARGUS_WHATSAPP_TO", "")


def ensure_data_dir():
    """Create the database directory if it does not yet exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
