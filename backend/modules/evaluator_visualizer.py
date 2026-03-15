import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class EvaluatorVisualizer:
    def rmse(self, preds, truths):
        return np.sqrt(np.mean((preds-truths)**2))

    def precision_at_k(self, pred_indices, true_indices, k=10):
        return len(set(pred_indices[:k]) & set(true_indices))/k

    def recall_at_k(self, pred_indices, true_indices, k=10):
        return len(set(pred_indices[:k]) & set(true_indices))/len(true_indices)

    def visualize_matrices(self, user_sim, item_sim, content_sim, latent_pred):
        self._plot_matrix(user_sim,"User Similarity")
        self._plot_matrix(item_sim,"Item Similarity")
        self._plot_matrix(content_sim,"Content Similarity")
        self._plot_matrix(latent_pred,"Latent Factors")

    def _plot_matrix(self, matrix, title):
        plt.figure(figsize=(6,5))
        sns.heatmap(matrix,cmap='viridis',annot=False)
        plt.title(title)
        plt.show()

