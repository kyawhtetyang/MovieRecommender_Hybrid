import json
from modules.pipeline import Pipeline
from modules.data_manager import DataManager

with open("config/config.json") as f:
    config = json.load(f)

dm = DataManager(config)
dm.init_db()

pipeline = Pipeline(config)
pipeline.run_hybrid_weights()

