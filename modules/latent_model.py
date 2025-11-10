import numpy as np
import pandas as pd
from scipy.sparse.linalg import svds

class LatentModel:
    def __init__(self, n_factors=8):
        """
        n_factors: number of latent features
        """
        self.n_factors = n_factors
        self.user_factors = None
        self.item_factors = None
        self.user_means = None

    def train(self, ratings_matrix):
        """
        Train latent factor model using SVD.
        ratings_matrix: pd.DataFrame (users x items) with normalized ratings
        Returns: predicted ratings matrix (numpy array)
        """
        # Convert DataFrame to numpy array
        R = ratings_matrix.to_numpy(dtype=np.float64)

        # Compute user means
        self.user_means = R.mean(axis=1)  # ndarray

        # Demean ratings
        R_demeaned = R - self.user_means.reshape(-1, 1)

        # Determine safe k for SVD
        max_k = min(R_demeaned.shape) - 1
        if max_k < 1:
            raise ValueError("Not enough users or items for SVD. Require min(users,items) >= 2")
        k = min(self.n_factors, max_k)

        # Compute SVD
        U, sigma, Vt = svds(R_demeaned, k=k)
        sigma_matrix = np.diag(sigma)

        # Reconstruct predicted ratings
        R_pred = np.dot(np.dot(U, sigma_matrix), Vt) + self.user_means.reshape(-1, 1)

        # Save factors
        self.user_factors = U
        self.item_factors = Vt.T  # items x latent
        return R_pred

    def predict_user(self, user_index):
        """
        Return predicted ratings for a single user index.
        """
        if self.user_factors is None or self.item_factors is None:
            raise ValueError("Model not trained yet")
        return np.dot(self.user_factors[user_index, :], self.item_factors.T) + self.user_means[user_index]

