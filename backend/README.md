# Gmail Clone — Backend

FastAPI backend for the Gmail Clone project (`api / domain / services / infrastructure / core` layering, SQLite, JWT auth, ML wired per `BACKEND_INTEGRATION.md`).

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
copy .env.example .env       # Windows: copy, macOS/Linux: cp
```

Edit `.env` and set a real `SECRET_KEY` (any long random string is fine for local dev).

## Run

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Interactive docs (Swagger UI): http://localhost:8000/docs
- On first run, SQLite tables are created automatically (no migrations needed — `Base.metadata.create_all()`).

## Test

```bash
pytest -v
```

15 tests covering signup/login, email send/list/get, folder filtering, search, mark-as-read, and the ML contract (`test_ml_integration.py`, matching section 7 of `BACKEND_INTEGRATION.md`).

## Wiring in the real ML models

Right now `app/ml/inference.py` auto-falls-back to the Phase 1 stub values (`is_spam=False`, `priority_score=0.5`) because no `.pkl` files exist yet. To go live:

1. Drop `spam_model.pkl`, `vectorizer.pkl`, `priority_model.pkl` into `app/ml/artifacts/`.
2. Either keep this `inference.py` (it already loads them automatically — see `_load_artifacts()`), or replace it wholesale with ML's own version if their function internals differ. The two functions' signatures/contract stay identical either way, so nothing else in the backend needs to change.
3. Re-run `pytest` — `test_ml_integration.py` will now be exercising the real models instead of the stub.

## Design decisions worth knowing about

**Folder semantics.** The DB schema (per the project plan) has a single `folder` field per `Email` row — there's no separate row per mailbox. So:
- `GET /emails?folder=sent` returns emails where **you are the sender**, regardless of the `folder` column (which reflects the *recipient's* spam/inbox classification, not yours).
- `GET /emails?folder=inbox` / `folder=spam` returns emails where **you are the recipient**, filtered by that column.

This means "sent" isn't a database value ML/the classifier ever sets — it's a query-time perspective. Flagging this because it's a design choice, not something spelled out explicitly in the project plan.

**Priority feature computation** (`sender_frequency`, `reply_rate`) is computed from the **recipient's** perspective — i.e. "does *this recipient* usually get email from this sender / reply to them" — since the resulting `priority_score` is what sorts *their* inbox. See `_compute_priority_features()` in `app/services/email_service.py`.

**Auth:** `passlib[bcrypt]` for hashing + `python-jose` for JWT. `bcrypt` is pinned to `4.0.1` in `requirements.txt` — newer bcrypt (4.1+) breaks passlib 1.7.4's internal version-detection and throws on hash. If you ever bump this, either bump `passlib` too or watch for that exact failure.

**No Alembic.** Given the "keep it simple" theme, schema changes just mean re-running with a fresh `.db` file during development. If the schema needs to evolve after real data exists, that's the point to introduce Alembic.

## Project structure

```
app/
├── core/            # config (env vars), security (hashing, JWT)
├── domain/           # pure business rules & enums, no DB/framework deps
├── infrastructure/    # SQLAlchemy engine/session + ORM models
├── services/          # business logic (auth_service, email_service) — talks to DB + ML
├── ml/                # inference.py + artifacts/ (from ML teammate)
├── api/
│   ├── deps.py         # get_db, get_current_user
│   ├── schemas/         # Pydantic request/response models
│   └── routers/          # auth.py, emails.py — thin, delegate to services
└── main.py             # app creation, CORS, router registration
tests/                  # pytest, isolated in-memory SQLite per test
```
