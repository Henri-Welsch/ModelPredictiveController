from __future__ import annotations

from PythonLinearNonlinearControl.models.base_model import Model
from PythonLinearNonlinearControl.models.composite_models.predictors.base_predictor import Predictor


class GreenhouseCompositeModel(Model):
    """
    A composite model that integrates multiple single-target predictors.
    This acts as the 'Composite' in the Composite pattern, managing a collection
    of SingleTargetPredictor objects.
    """

    def __init__(self, predictors: dict[str,  Predictor]):
        """
        Args:
            predictors (list[SingleTargetPredictor]): A list of predictors, one for each state variable.
        """
        super(GreenhouseCompositeModel, self).__init__()
        self.predictors: dict[str, Predictor] = predictors


    def predict_next_state(self, curr_x, u):
        pass
