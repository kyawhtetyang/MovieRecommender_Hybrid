import numpy as np

class HybridRecommender:
    def recommend(
        self,
        user_idx,
        ratings_matrix,
        user_sim,
        item_sim,
        content_sim,
        latent_pred,
        movies_df,
        embeddings=None,
        weights=None,
        top_k=10
    ):
        """
        Compute top-k hybrid recommendations for a given user.
        """
        weights = weights or {'user':0.25,'item':0.25,'content':0.25,'latent':0.25}

        n_users, n_items = ratings_matrix.shape

        # Ensure content_sim aligns
        if content_sim.shape[0] != n_items or content_sim.shape[1] != n_items:
            padded = np.eye(n_items)
            min_r, min_c = content_sim.shape
            padded[:min_r, :min_c] = content_sim
            content_sim = padded

        # Compute scores
        user_scores = np.dot(user_sim[user_idx], ratings_matrix)
        item_scores = np.dot(ratings_matrix[user_idx], item_sim)
        content_scores = np.dot(ratings_matrix[user_idx], content_sim)
        latent_scores = latent_pred[user_idx]

        final_scores = (
            weights.get('user',0.25)*user_scores +
            weights.get('item',0.25)*item_scores +
            weights.get('content',0.25)*content_scores +
            weights.get('latent',0.25)*latent_scores
        )

        # Diversity penalty
        if embeddings is not None and embeddings.shape[0] == n_items:
            norms = np.linalg.norm(embeddings, axis=1) + 1e-8
            emb_sim = (embeddings @ embeddings.T) / (norms[:,None]*norms[None,:])
            np.fill_diagonal(emb_sim, 0)
            div_penalty = emb_sim.mean(axis=0)
            if div_penalty.shape == final_scores.shape:
                final_scores -= 0.1 * div_penalty

        # Mask already rated items
        final_scores[ratings_matrix[user_idx] > 0] = -np.inf

        # Select top-k safely
        top_indices = np.argsort(final_scores)[-top_k:][::-1]
        top_indices = top_indices[top_indices < len(movies_df)]  # clip to valid range

        # Detect movie ID column
        movie_id_col = next((col for col in ['movieId','movie_id','id'] if col in movies_df.columns), None)
        if movie_id_col is None:
            raise ValueError(f"No movie ID column found. Columns: {movies_df.columns.tolist()}")

        # Return movie IDs
        movie_ids = movies_df[movie_id_col].iloc[top_indices].tolist()
        return movie_ids

    # Optimize hybrid weights via brute-force grid search
    def optimize_weights(self, user_item, user_sim, item_sim, content_sim, latent_pred):
        """
        Brute-force search over 0,0.25,0.5,0.75,1 for each component
        Returns best_weights dict
        """
        n_users, n_items = user_item.shape

        # Ensure content_sim aligns with user_item
        if content_sim.shape[0] != n_items or content_sim.shape[1] != n_items:
            padded = np.eye(n_items)
            min_r, min_c = content_sim.shape
            padded[:min_r, :min_c] = content_sim
            content_sim = padded

        predictions = {
            'user': user_sim @ user_item,
            'item': user_item @ item_sim,
            'content': user_item @ content_sim,
            'latent': latent_pred
        }

        true_ratings = user_item
        best_rmse = float('inf')
        best_weights = {'user':0.25,'item':0.25,'content':0.25,'latent':0.25}

        # brute-force grid search
        for u in np.linspace(0,1,5):
            for i in np.linspace(0,1-u,5):
                for c in np.linspace(0,1-u-i,5):
                    l = 1-u-i-c
                    pred = u*predictions['user'] + i*predictions['item'] + c*predictions['content'] + l*predictions['latent']
                    rmse = np.sqrt(np.mean((pred-true_ratings)**2))
                    if rmse < best_rmse:
                        best_rmse = rmse
                        best_weights = {'user':u,'item':i,'content':c,'latent':l}

        return best_weights

