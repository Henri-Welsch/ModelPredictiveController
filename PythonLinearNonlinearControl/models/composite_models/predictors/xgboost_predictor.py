import numpy as np
import xgboost

from .base_predictor import Predictor

class XGBoostPredictor(Predictor):
    def __init__(self, booster):
        self._booster = booster

    def predict(self, features: list[float]) -> float:
        X = np.asarray(features, dtype=float).reshape(1, -1)
        dmat = xgboost.DMatrix(X, feature_names=self.get_feature_names())
        pred = self._booster.predict(dmat)
        return float(pred[0])

    def predict_batch(self, features: np.ndarray) -> np.ndarray:
        """
        Args:
            features: array-like of shape (batch_size, n_features)
        Returns:
            preds: np.ndarray of shape (batch_size,)
        """
        X = np.asarray(features, dtype=float)
        if X.ndim != 2:
            raise ValueError(f"features must be 2D (batch_size, n_features), got shape {X.shape}")
        dmat = xgboost.DMatrix(X, feature_names=self.get_feature_names())
        pred = self._booster.predict(dmat)
        return np.asarray(pred, dtype=float).reshape(-1)

    def get_feature_names(self) -> list[str]:
        return self._booster.feature_names