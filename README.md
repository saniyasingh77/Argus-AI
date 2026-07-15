# 👁️ Argus AI

> **Always Watching. Always Protecting.**

Argus AI is an AI-powered patient monitoring system that uses Computer Vision and Deep Learning to monitor patients in real time, detect emergency situations, and generate alerts.

---

## Features

- 🔐 User & Admin Login
- 📹 Live Patient Monitoring
- 🎥 Video Upload Analysis
- 🤖 AI Activity Detection
- 🚨 Emergency Detection
- 📊 Activity Reports
- 📱 WhatsApp Alerts
- 📧 Email Notifications
- 💾 SQLite Database
- 🧠 Deep Learning + MediaPipe Pose Detection

---

## Tech Stack

- Python
- Flask
- OpenCV
- MediaPipe
- TensorFlow
- HTML
- CSS
- JavaScript
- SQLite

---

## Project Structure

```
Argus-AI/
│
├── backend/
├── frontend/
├── database/
├── train/
├── requirements.txt
└── README.md
```

---

## Demo logins

| Role  | Email             | Password   |
|-------|-------------------|------------|
| User  | demo@argus.ai     | `demo123`  |
| Admin | admin@argus.ai    | `admin123` |

These are auto-created (with sample activity data) when `ARGUS_SEED_DEMO=true`.

## How to Run

### 1. Local — web tier only (lightweight)

```bash
python -m venv .venv
.venv/Scripts/activate                 # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
python -m backend.api_server
```

Open http://127.0.0.1:5000 and log in with a demo account (seeded automatically).

### 2. Local — full stack with camera (falls, live monitoring, video analysis)

```bash
pip install -r requirements-ml.txt     # OpenCV + MediaPipe + TensorFlow
python -m backend.api_server
```

> Live-camera monitoring and video CV analysis need a local webcam + the ML
> stack. The hosted web tier (UI, auth, reports, alerts) runs without them and
> degrades gracefully (those buttons show a friendly message in the cloud).

### 3. Docker

```bash
cp .env.example .env                   # optional: real alert secrets
docker compose up --build
```

Open http://localhost:5000 — health probe at `/health`.

The image runs under **gunicorn** as a non-root user, persists SQLite to a
volume, ships a container `HEALTHCHECK`, and installs only the tiny
`requirements.txt` (no camera/GPU libs) so it stays small and deployable
anywhere.

### 4. Deploy free on Render

This repo includes a [`render.yaml`](render.yaml) blueprint.

1. Push this repo to your GitHub account.
2. Go to **dashboard.render.com → New → Blueprint** and pick the repo.
3. Render builds the `Dockerfile` and gives you a public
   `https://<name>.onrender.com` URL. Log in with a demo account above.

(Free instances sleep after inactivity and reset the SQLite DB on restart;
`ARGUS_SEED_DEMO=true` re-creates the demo login + data on every start.)

---

## Configuration

All runtime config and secrets come from environment variables — nothing is
hard-coded. See [`.env.example`](.env.example). Key variables:

| Variable | Purpose |
|----------|---------|
| `ARGUS_PORT` / `ARGUS_HOST` | Web server bind |
| `ARGUS_DB_PATH` / `ARGUS_DATA_DIR` | SQLite location (mount a volume in prod) |
| `ARGUS_SEED_DEMO` | Seed demo logins + sample activity on startup |
| `ARGUS_EMAIL_*` | SMTP email alerts |
| `ARGUS_TWILIO_*` / `ARGUS_WHATSAPP_*` | Twilio WhatsApp alerts |

---

## CI/CD

`.github/workflows/ci.yml` runs on every push/PR to `main`:

1. **Lint & Test** — byte-compile + `pytest`
2. **Security Scans** — `gitleaks` secret scan (fails on any secret) + `pip-audit` dependency CVE report
3. **Build & Scan Image** — Docker build + **Trivy** image vulnerability scan
4. **Publish** — pushes the image to GHCR on `main` (least-privilege `packages: write`)

---

## Security note

Earlier revisions committed live email/Twilio credentials. They have been
moved to environment variables, **but any secret ever committed must be
rotated** (revoke the Gmail app password, regenerate the Twilio token) and the
git history scrubbed (`git filter-repo`), since it remains recoverable from
history.

---

## Future Scope

- ✅ Cloud Deployment using Docker (done)
- ✅ Secure CI/CD pipeline (done)
- Kubernetes Support
- Multi-Patient Monitoring
- Mobile Application
- Doctor Dashboard
- Real-time Analytics

---

## Developed By

**Saniya Singh**


