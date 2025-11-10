from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import json
import time
from modules.pipeline import Pipeline
from modules.data_manager import DataManager
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Load config
with open("config/config.json") as f:
    config = json.load(f)

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Initialize pipeline and DB
pipeline = Pipeline(config)
dm = DataManager(config)
dm.init_db()

# Helper to get DB connection
def get_db():
    conn = sqlite3.connect(config['database_file'])
    conn.row_factory = sqlite3.Row
    return conn

# Routes

@app.route("/")
def home():
    conn = get_db()
    users = conn.execute("SELECT id FROM users").fetchall()
    conn.close()
    return render_template("home.html", users=users)

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed = generate_password_hash(password)
        conn = get_db()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username,password) VALUES (?,?)", (username, hashed))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists"
    return render_template("signup.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Map to matrix index
    try:
        user_idx = dm.user_id_to_index(user_id)
    except ValueError:
        return "User not found in DB"

    # Predict top recommendations
    top_movies_ids = pipeline.predict_for_user(user_idx)

    conn = get_db()
    movies = []
    if top_movies_ids:
        placeholders = ",".join("?"*len(top_movies_ids))
        query = f"SELECT * FROM movies WHERE movie_id IN ({placeholders})"
        movies = conn.execute(query, top_movies_ids).fetchall()
    conn.close()

    return render_template("dashboard.html", user_id=user_id, movies=movies)

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("home"))

@app.route("/rate", methods=["GET","POST"])
def rate():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method=="POST":
        user_id = session.get("user_id")
        movie_id = int(request.form["movie_id"])
        rating = float(request.form["rating"])
        timestamp = int(time.time())

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM movies WHERE movie_id=?", (movie_id,))
        if c.fetchone()[0]==0:
            conn.close()
            return "Invalid movie ID"

        c.execute("INSERT INTO ratings (user_id, movie_id, rating, timestamp) VALUES (?,?,?,?)",
                  (user_id, movie_id, rating, timestamp))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))

    return render_template("rate.html")

@app.route("/recommend")
def recommend():
    user_id = request.args.get("user_id", type=int)
    if user_id is None:
        return "User ID not provided"

    try:
        user_idx = dm.user_id_to_index(user_id)
    except ValueError:
        return "User not found"

    top_movies_ids = pipeline.predict_for_user(user_idx)
    conn = get_db()
    movies = []
    if top_movies_ids:
        placeholders = ",".join("?"*len(top_movies_ids))
        query = f"SELECT * FROM movies WHERE movie_id IN ({placeholders})"
        movies = conn.execute(query, top_movies_ids).fetchall()
    conn.close()

    return render_template("recommend.html", movies=movies)

# Run server
if __name__=="__main__":
    app.run(debug=True)


