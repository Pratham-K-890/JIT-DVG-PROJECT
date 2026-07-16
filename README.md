# Gmail Clone

A full-stack Gmail-style webmail clone built as a learning project: a FastAPI backend with JWT auth and SQLite, a React + TypeScript (Vite) frontend styled after Gmail, and two small ML models (spam detection, priority scoring) run inline inside the backend — no separate ML service.

## Stack

| Layer    | Tech |
|----------|------|
| Frontend | React 19, TypeScript, Vite, React Router |
| Backend  | FastAPI, SQLAlchemy 2.0, SQLite, JWT (python-jose), bcrypt (passlib) |
| ML       | scikit-learn models (spam classifier + priority regressor), loaded from `.pkl` artifacts at backend import time |

## Project structure

```
backend/    FastAPI app (api / domain / services / infrastructure / core layering)
frontend/   React + Vite SPA (entities / features / pages / widgets)
```

Each has its own README with more detail: [`backend/README.md`](backend/README.md), [`frontend/README.md`](frontend/README.md).

## Running locally

You need both the backend and frontend running at the same time.

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
copy .env.example .env       # Windows: copy, macOS/Linux: cp .env.example .env
```

Edit `.env` and set a real `SECRET_KEY` (any long random string works for local dev).

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- SQLite tables are created automatically on first run.

### 2. Frontend (React + Vite)

```bash
cd frontend
npm install
```

Create a `frontend/.env` file (there is no `.env.example` for this yet) with the backend URL:

```
VITE_API_BASE_URL=http://localhost:8000
```

```bash
npm run dev
```

- App: http://localhost:5173

## Features

- Signup / login with JWT-based auth
- Compose, send, and read emails
- Inbox / Sent / Spam folders (see the "Folder semantics" note in [`backend/README.md`](backend/README.md) — "sent" is computed at query time, not a stored folder value)
- Search across subject/body
- Spam classification and priority scoring applied automatically to incoming mail via the bundled ML models
- Sort inbox by priority score

## Known gaps

- The backend `tests/` folder referenced in `backend/README.md` was removed from the repo (see git history) — there is currently no automated test suite to run.
- `app/ml/inference.py` loads the three `.pkl` artifacts unconditionally at import time. The in-repo docs describe a lazy-load/stub-fallback behavior for missing artifacts that isn't actually implemented — it only works today because the trained `.pkl` files are committed under `backend/app/ml/artifacts/`.
- No Alembic/migrations — schema changes currently mean dropping and recreating the local `.db` file.
