Drop the trained model files here, exactly as named:

- spam_model.pkl
- vectorizer.pkl
- priority_model.pkl

`app/ml/inference.py` auto-detects them at runtime (lazy-loaded on first call).
Until they exist, `predict_spam()` / `predict_priority()` fall back to the
Phase 1 stub values (`False` / `0.5`) automatically — no code changes needed
either way.
