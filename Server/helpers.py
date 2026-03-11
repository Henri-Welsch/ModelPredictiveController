from pathlib import Path

import xgboost

from PythonLinearNonlinearControl.models.composite_models.predictors.base_predictor import Predictor
from PythonLinearNonlinearControl.models.composite_models.predictors.xgboost_predictor import XGBoostPredictor


def load_boosters(folder_path: Path) -> dict[str, Predictor]:
    """
    Load all XGBoost models (*.json) from a folder and return
    Predictor adapters keyed by booster name.

    References:
        https://docs.python.org/3/library/pathlib.html
        https://xgboost.readthedocs.io/en/stable/python/python_intro.html
    Example:
        "temperature.json" -> predictors["temperature"] = XGBoostPredictor(...)
    """
    booster_paths = list(folder_path.glob("*.json"))
    predictors = {}

    for booster_path in booster_paths:
        booster = xgboost.Booster()
        booster.load_model(booster_path)

        name = booster_path.stem
        predictors[name] = XGBoostPredictor(booster)

    return predictors
