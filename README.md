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
conda activate tf
python train.py
python train_hybrid_weights.py
python app.py
# then open http://127.0.0.1:5000

# Optional: Command line prediction
python main.py --user 1 --visualize
python predict.py


