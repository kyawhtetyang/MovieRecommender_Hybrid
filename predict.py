import json
from modules.pipeline import Pipeline

with open("config/config.json") as f:
    config = json.load(f)

pipeline = Pipeline(config)
pipeline.predict_for_user(user_idx=0, visualize=False)

