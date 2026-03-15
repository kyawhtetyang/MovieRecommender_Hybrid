from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class SimilarityModels:
    def compute_all(self, user_item, movies_df):
        user_sim = self.compute_user_similarity(user_item)
        item_sim = self.compute_item_similarity(user_item)
        content_sim = self.compute_content_similarity(movies_df)
        return user_sim, item_sim, content_sim

    def compute_user_similarity(self, ratings_matrix):
        sim = cosine_similarity(ratings_matrix)
        np.fill_diagonal(sim, 0)
        return sim

    def compute_item_similarity(self, ratings_matrix):
        sim = cosine_similarity(ratings_matrix.T)
        np.fill_diagonal(sim, 0)
        return sim

    def compute_content_similarity(self, movies_df):
        tfidf = TfidfVectorizer(stop_words='english')
        content_matrix = tfidf.fit_transform(movies_df['genres'])
        sim = cosine_similarity(content_matrix)
        np.fill_diagonal(sim, 0)
        return sim

