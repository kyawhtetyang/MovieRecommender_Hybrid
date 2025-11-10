import os
import time
import numpy as np
import pandas as pd
import sqlite3

class DataManager:
    def __init__(self, config):
        self.config = config
        self.movies_df = None
        self.ratings_df = None

    # ---------------- DB INIT ----------------
    def init_db(self):
        """Initialize SQLite DB and preload CSVs safely."""
        db_path = self.config['database_file']
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # ===== CREATE TABLES =====
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT)''')

        c.execute('''CREATE TABLE IF NOT EXISTS ratings (
            user_id INTEGER, movie_id INTEGER, rating REAL, timestamp INTEGER)''')

        c.execute('''CREATE TABLE IF NOT EXISTS movies (
            movie_id INTEGER PRIMARY KEY, title TEXT, genres TEXT, year INTEGER)''')

        conn.commit()

        # ===== LOAD MOVIES =====
        if c.execute("SELECT COUNT(*) FROM movies").fetchone()[0] == 0:
            self._preload_movies(c)

        # ===== LOAD RATINGS =====
        if c.execute("SELECT COUNT(*) FROM ratings").fetchone()[0] == 0:
            self._preload_ratings(c)

        conn.commit()
        conn.close()

    def _preload_movies(self, cursor):
        movies_csv = "data/movies.csv"
        if os.path.exists(movies_csv):
            df = pd.read_csv(movies_csv)
            df.rename(columns=lambda x: x.strip(), inplace=True)
            for _, row in df.iterrows():
                cursor.execute('''INSERT OR IGNORE INTO movies (movie_id, title, genres, year)
                                  VALUES (?,?,?,?)''',
                               (int(row.movieId), row.title, row.genres, int(row.year)))

    def _preload_ratings(self, cursor):
        ratings_csv = "data/ratings.csv"
        if os.path.exists(ratings_csv):
            df = pd.read_csv(ratings_csv)
            df.rename(columns=lambda x: x.strip(), inplace=True)

            # Safe numeric conversion
            def safe_float(x):
                if isinstance(x, bytes):
                    return float(np.frombuffer(x, dtype=np.float64)[0])
                return float(x)

            df['rating'] = pd.to_numeric(df['rating'].apply(safe_float), errors='coerce')
            df.dropna(subset=['rating'], inplace=True)
            df['userId'] = df['userId'].astype(int)
            df['movieId'] = df['movieId'].astype(int)
            df['timestamp'] = df['timestamp'].astype(int)

            for _, row in df.iterrows():
                cursor.execute('''INSERT INTO ratings (user_id, movie_id, rating, timestamp)
                                  VALUES (?,?,?,?)''',
                               (row.userId, row.movieId, row.rating, row.timestamp))

    # ---------------- DATA LOADING ----------------
    def load_and_preprocess(self):
        """Load ratings and movies from DB, normalize ratings."""
        conn = sqlite3.connect(self.config['database_file'])
        ratings = pd.read_sql_query("SELECT * FROM ratings", conn)
        movies = pd.read_sql_query("SELECT * FROM movies", conn)
        conn.close()

        # Ensure numeric
        ratings['rating'] = pd.to_numeric(ratings['rating'], errors='coerce')
        ratings.dropna(subset=['rating'], inplace=True)

        # Normalize ratings per user
        ratings['rating_norm'] = ratings.groupby('user_id')['rating'].transform(lambda x: x - x.mean())

        self.ratings_df = ratings
        self.movies_df = movies
        return ratings, movies

    def normalize_ratings(self, ratings):
        if ratings.empty:
            return ratings
        ratings['rating_norm'] = ratings.groupby('user_id')['rating'].transform(lambda x: x - x.mean())
        return ratings

    def apply_temporal_decay(self, ratings, decay_factor=0.9):
        ratings = ratings.copy()
        max_ts = ratings['timestamp'].max() if not ratings.empty else int(time.time())
        ratings['time_weight'] = decay_factor ** ((max_ts - ratings['timestamp']) / (60*60*24))
        ratings['rating_weighted'] = ratings['rating_norm'] * ratings['time_weight']
        return ratings

    # ---------------- MATRIX I/O ----------------
    def save_outputs(self, user_item, user_sim, item_sim, content_sim, latent_pred):
        out = self.config['output_dir']
        os.makedirs(out, exist_ok=True)
        np.save(os.path.join(out, 'user_item.npy'), user_item)
        np.save(os.path.join(out, 'user_sim.npy'), user_sim)
        np.save(os.path.join(out, 'item_sim.npy'), item_sim)
        np.save(os.path.join(out, 'content_sim.npy'), content_sim)
        np.save(os.path.join(out, 'latent_factors.npy'), latent_pred)

    def load_matrices(self):
        out = self.config['output_dir']
        return (
            np.load(os.path.join(out, 'user_item.npy')),
            np.load(os.path.join(out, 'user_sim.npy')),
            np.load(os.path.join(out, 'item_sim.npy')),
            np.load(os.path.join(out, 'content_sim.npy')),
            np.load(os.path.join(out, 'latent_factors.npy'))
        )

    # ---------------- EMBEDDINGS ----------------
    def load_embeddings(self):
        path = self.config.get('embedding_file')
        if not path:
            return None

        os.makedirs(os.path.dirname(path), exist_ok=True)

        if os.path.exists(path):
            try:
                embeddings = np.load(path)
                if embeddings.dtype == object:
                    raise ValueError("Invalid embedding dtype, regenerating")
                return embeddings
            except:
                print(f"[DataManager] Regenerating embeddings at {path}")

        # Regenerate random embeddings
        conn = sqlite3.connect(self.config['database_file'])
        ratings = pd.read_sql("SELECT * FROM ratings", conn)
        conn.close()
        n_users = ratings['user_id'].nunique()
        n_features = 8
        embeddings = np.random.rand(n_users, n_features)
        np.save(path, embeddings)
        return embeddings

    # Map user_id -> matrix row index
    def user_id_to_index(self, user_id):
        conn = sqlite3.connect(self.config['database_file'])
        df = pd.read_sql("SELECT DISTINCT user_id FROM ratings ORDER BY user_id", conn)
        conn.close()
        try:
            return df.index[df['user_id']==user_id][0]
        except IndexError:
            raise ValueError(f"User {user_id} not found")

