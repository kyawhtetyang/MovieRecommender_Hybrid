# Movie Recommender (Hybrid) - Monorepo

This repo is split into:

- `backend/` - Flask web app, hybrid recommender, demo SQLite DB.
- `frontend/` - Static landing page (placeholder for future UI upgrade).

## Backend quick start

```bash
cd backend
pip install -r requirements.txt
cp config/config.example.json config/config.json
export FLASK_SECRET_KEY="your-secret"
python app.py
```

Demo login:

- username: `demo`
- password: `demo1234`

## Frontend

The frontend folder contains a simple static landing page you can deploy to Vercel.
See `frontend/README.md` for details.
