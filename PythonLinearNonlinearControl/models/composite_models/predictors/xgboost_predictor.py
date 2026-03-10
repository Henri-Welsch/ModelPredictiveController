import numpy as np

from .base_predictor import Predictor


class XGBoostPredictor(Predictor):
    def __init__(self, booster):
        self._booster = booster

    def predict(self, features: list[float]) -> list[float]:
        return self._booster.predict(features)

    def get_feature_names(self) -> list[str]:
        return self._booster.feature_names



