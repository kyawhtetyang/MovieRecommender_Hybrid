# 🎬 Movie Recommendation System v8 — Flask Web MVP

Features:

1. Web interface (Flask) with home, dashboard, rate, signup/login, recommend pages
2. SQLite database for users, ratings, movies
3. Hybrid recommendation engine (user/item/content/latent)
4. Dynamic recommendations after ratings
5. Logging and error tracking
6. MVP ready for future analytics & REST API

Run:

```bash
cd backend
conda activate tf
pip install -r requirements.txt
pip install -r requirements-train.txt
cp config/config.example.json config/config.json
# optional: export FLASK_SECRET_KEY="your-secret"
python train.py
python train_hybrid_weights.py
python app.py
# then open http://127.0.0.1:5000

# Optional: Command line prediction
python main.py --user 1 --visualize
python predict.py
```

Configuration:

- `data/demo.db` is included for a quick demo (sample users, ratings, movies).
- `config/config.json` is required for local runs and is not committed.
- For demo-only runs (no training), `requirements.txt` is sufficient.
- You can also override config values with env vars:
  - `DATABASE_FILE` (default: `data/demo.db`)
  - `OUTPUT_DIR` (default: `output`)
  - `EMBEDDING_FILE` (default: `output/embeddings.npy`)
- Set `FLASK_SECRET_KEY` in production.
