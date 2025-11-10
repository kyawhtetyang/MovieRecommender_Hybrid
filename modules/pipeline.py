from modules.data_manager import DataManager
from modules.similarity_models import SimilarityModels
from modules.latent_model import LatentModel
from modules.hybrid_recommender import HybridRecommender
from modules.evaluator_visualizer import EvaluatorVisualizer

class Pipeline:
    def __init__(self, config):
        self.config = config
        self.data_manager = DataManager(config)
        self.sim_models = SimilarityModels()
        self.latent_model = LatentModel()
        self.hybrid = HybridRecommender()
        self.evaluator = EvaluatorVisualizer()
        self.movies_df = None  # will hold movies metadata

    # TRAINING PIPELINE
    def run_training(self):
        """
        Loads data, computes similarity matrices, trains latent model,
        and saves all matrices for later use.
        """
        # Load & preprocess
        user_item, movies_df = self.data_manager.load_and_preprocess()
        self.movies_df = movies_df

        # Compute similarity matrices
        user_sim, item_sim, content_sim = self.sim_models.compute_all(user_item, movies_df)

        # Train latent model
        latent_pred = self.latent_model.train(user_item)

        # Save outputs
        self.data_manager.save_outputs(user_item, user_sim, item_sim, content_sim, latent_pred)
        print("Training finished. All matrices saved.")

    # HYBRID WEIGHTS OPTIMIZATION
    def run_hybrid_weights(self):
        """
        Loads matrices and performs brute-force grid search
        to find optimal hybrid weights.
        """
        user_item, user_sim, item_sim, content_sim, latent_pred = self.data_manager.load_matrices()
        weights = self.hybrid.optimize_weights(user_item, user_sim, item_sim, content_sim, latent_pred)
        print("Optimal hybrid weights:", weights)
        return weights

    # PREDICTION PIPELINE
    def predict_for_user(self, user_idx, visualize=False):
        """
        Returns top recommended movie IDs for a given user.
        Handles missing movies_df automatically.
        """
        # Ensure movies_df is loaded
        if self.movies_df is None:
            _, self.movies_df = self.data_manager.load_and_preprocess()

        # Load matrices & embeddings
        user_item, user_sim, item_sim, content_sim, latent_pred = self.data_manager.load_matrices()
        embeddings = self.data_manager.load_embeddings()

        # Recommend top movies
        top_movies = self.hybrid.recommend(
            user_idx=user_idx,
            ratings_matrix=user_item,
            user_sim=user_sim,
            item_sim=item_sim,
            content_sim=content_sim,
            latent_pred=latent_pred,
            movies_df=self.movies_df,
            embeddings=embeddings
        )

        # Optional visualization
        if visualize:
            self.evaluator.visualize_matrices(user_sim, item_sim, content_sim, latent_pred)

        print(f"Top recommended movie IDs for user {user_idx}:", top_movies)
        return top_movies
