from abc import ABC, abstractmethod

import numpy as np


class Predictor(ABC):

    @abstractmethod
    def predict(self, features: list[float]) -> list[float]:
        """Predict a scalar target given a 1D feature vector."""
        pass

    @abstractmethod
    def get_feature_names(self) -> list[str]:
        """
        Names of features required by this predictor, in the exact order expected
        by `predict(features)`.

        Examples:
          ["Tin", "RHin", "Tout", "u.window_open", "u.fan_speed"]
          ["Tout"]   (for a trivial outside temperature predictor)

        The composite model uses this to build the feature vector robustly.

        TODO(delta-models):
          Once you switch to delta prediction, keep this contract unchanged;
          only the interpretation of the output changes.
        """
        pass