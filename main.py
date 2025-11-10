import json
import argparse
from modules.pipeline import Pipeline
from modules.data_manager import DataManager

with open("config/config.json") as f:
    config = json.load(f)

dm = DataManager(config)
dm.init_db()

parser = argparse.ArgumentParser()
parser.add_argument("--user", type=int, required=True)
parser.add_argument("--visualize", action='store_true')
args = parser.parse_args()

pipeline = Pipeline(config)
pipeline.run_training()
pipeline.run_hybrid_weights()

# safe mapping user_id -> row index
user_idx = dm.user_id_to_index(args.user)
pipeline.predict_for_user(user_idx, visualize=args.visualize)

