from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_CONFIG: dict[str, Any] = {
    "database_file": "data/demo.db",
    "output_dir": "output",
    "embedding_file": "output/embeddings.npy",
}


def _resolve_path(base_dir: Path, value: str) -> str:
    candidate = Path(value)
    if candidate.is_absolute():
        return str(candidate)
    return str((base_dir / candidate).resolve())


def load_config() -> dict[str, Any]:
    base_dir = Path(__file__).resolve().parent
    config_path = os.getenv("MOVIE_RECOMMENDER_CONFIG", "config/config.json")
    resolved_path = Path(config_path)
    if not resolved_path.is_absolute():
        resolved_path = (base_dir / resolved_path).resolve()

    if resolved_path.is_file():
        with resolved_path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
    else:
        config = dict(DEFAULT_CONFIG)

    env_db = os.getenv("DATABASE_FILE")
    env_output = os.getenv("OUTPUT_DIR")
    env_embedding = os.getenv("EMBEDDING_FILE")

    if env_db:
        config["database_file"] = env_db
    if env_output:
        config["output_dir"] = env_output
    if env_embedding:
        config["embedding_file"] = env_embedding

    config["database_file"] = _resolve_path(base_dir, str(config.get("database_file", DEFAULT_CONFIG["database_file"])))
    config["output_dir"] = _resolve_path(base_dir, str(config.get("output_dir", DEFAULT_CONFIG["output_dir"])))
    if config.get("embedding_file"):
        config["embedding_file"] = _resolve_path(base_dir, str(config.get("embedding_file")))

    return config
