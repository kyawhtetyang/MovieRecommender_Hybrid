from __future__ import annotations

import base64
import hashlib
import hmac
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from werkzeug.security import check_password_hash, generate_password_hash

from config_loader import load_config
from modules.data_manager import DataManager
from modules.pipeline import Pipeline


config = load_config()
pipeline = Pipeline(config)
dm = DataManager(config)
dm.init_db()

SECRET_KEY = os.getenv("API_SECRET_KEY") or os.getenv("FLASK_SECRET_KEY") or "movie-rec-dev-secret"
TOKEN_TTL_SECONDS = int(os.getenv("TOKEN_TTL_SECONDS", "86400"))

cors_origins = os.getenv("CORS_ORIGINS", "*")
if cors_origins.strip() in ("*", ""):
    allow_origins = ["*"]
else:
    allow_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app = FastAPI(title="Movie Recommender API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class RatingRequest(BaseModel):
    movie_id: int
    rating: float = Field(..., ge=0.0, le=5.0)


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(config["database_file"])
    conn.row_factory = sqlite3.Row
    return conn


def _encode_token(payload: str) -> str:
    signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    packed = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(packed.encode()).decode()


def _decode_token(token: str) -> Optional[int]:
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        user_id_str, issued_at_str, signature = decoded.split(":")
        payload = f"{user_id_str}:{issued_at_str}"
        expected = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        issued_at = int(issued_at_str)
        if int(time.time()) - issued_at > TOKEN_TTL_SECONDS:
            return None
        return int(user_id_str)
    except Exception:
        return None


def _require_user_id(authorization: Optional[str]) -> int:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    user_id = _decode_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_id


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/users")
def list_users() -> List[Dict[str, Any]]:
    conn = _get_db()
    rows = conn.execute("SELECT id, username FROM users ORDER BY id").fetchall()
    if not rows:
        rows = conn.execute("SELECT DISTINCT user_id FROM ratings ORDER BY user_id").fetchall()
        conn.close()
        return [{"id": row["user_id"], "username": f"user_{row['user_id']}"} for row in rows]
    users = [{"id": row["id"], "username": row["username"]} for row in rows]
    conn.close()
    return users


@app.post("/api/signup")
def signup(payload: SignupRequest) -> Dict[str, Any]:
    conn = _get_db()
    try:
        hashed = generate_password_hash(payload.password)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (payload.username, hashed),
        )
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Username already exists")
    finally:
        conn.close()
    return {"id": user_id, "username": payload.username}


@app.post("/api/login")
def login(payload: LoginRequest) -> Dict[str, Any]:
    conn = _get_db()
    user = conn.execute("SELECT id, username, password FROM users WHERE username = ?", (payload.username,)).fetchone()
    conn.close()
    if not user or not check_password_hash(user["password"], payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    issued_at = int(time.time())
    token = _encode_token(f"{user['id']}:{issued_at}")
    return {
        "token": token,
        "user": {"id": user["id"], "username": user["username"]},
    }


@app.get("/api/recommendations")
def recommendations(
    user_id: Optional[int] = Query(default=None, alias="user_id"),
    limit: int = Query(default=10, ge=1, le=50),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    resolved_user_id = user_id or _require_user_id(authorization)
    try:
        user_idx = dm.user_id_to_index(resolved_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    top_movie_ids = pipeline.predict_for_user(user_idx) or []
    if limit:
        top_movie_ids = top_movie_ids[:limit]

    results: List[Dict[str, Any]] = []
    if top_movie_ids:
        conn = _get_db()
        placeholders = ",".join("?" * len(top_movie_ids))
        rows = conn.execute(
            f"SELECT movie_id, title, genres, year FROM movies WHERE movie_id IN ({placeholders})",
            top_movie_ids,
        ).fetchall()
        conn.close()
        row_map = {row["movie_id"]: row for row in rows}
        for movie_id in top_movie_ids:
            row = row_map.get(movie_id)
            if not row:
                continue
            results.append(
                {
                    "movieId": row["movie_id"],
                    "title": row["title"],
                    "genres": row["genres"],
                    "year": row["year"],
                }
            )

    return {"userId": resolved_user_id, "results": results}


@app.post("/api/rate")
def rate_movie(payload: RatingRequest, authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    user_id = _require_user_id(authorization)
    conn = _get_db()
    cursor = conn.cursor()
    exists = cursor.execute("SELECT COUNT(*) FROM movies WHERE movie_id = ?", (payload.movie_id,)).fetchone()
    if not exists or exists[0] == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Movie not found")

    cursor.execute(
        "INSERT INTO ratings (user_id, movie_id, rating, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, payload.movie_id, payload.rating, int(time.time())),
    )
    conn.commit()
    conn.close()
    return {"status": "ok", "userId": user_id, "movieId": payload.movie_id}
