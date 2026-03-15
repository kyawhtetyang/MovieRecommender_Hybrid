from modules.pipeline import Pipeline
from config_loader import load_config

config = load_config()

pipeline = Pipeline(config)
pipeline.predict_for_user(user_idx=0, visualize=False)
