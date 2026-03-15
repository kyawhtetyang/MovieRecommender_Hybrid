from modules.pipeline import Pipeline
from modules.data_manager import DataManager
from config_loader import load_config

config = load_config()

dm = DataManager(config)
dm.init_db()

pipeline = Pipeline(config)
pipeline.run_hybrid_weights()
