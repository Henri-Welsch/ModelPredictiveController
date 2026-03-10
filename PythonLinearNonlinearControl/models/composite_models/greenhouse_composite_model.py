from __future__ import annotations

import numpy as np

from PythonLinearNonlinearControl.models.base_model import Model
from PythonLinearNonlinearControl.models.composite_models.predictors.base_predictor import Predictor


class GreenhouseCompositeModel(Model):
    """
    A composite model that integrates multiple single-target predictors.
    This acts as the 'Composite' in the Composite pattern, managing a collection
    of SingleTargetPredictor objects.
    """

    def __init__(self, predictors: dict[str,  Predictor], config):
        """
        Args:
            predictors (list[SingleTargetPredictor]): A list of predictors, one for each state variable.
        """
        super(GreenhouseCompositeModel, self).__init__()
        self.predictors: dict[str, Predictor] = predictors
        self.state_names = config.state_names
        self.input_names = config.action_names

    def predict_next_state(self, curr_x, u):
        curr_x = np.asarray(curr_x)
        u = np.asarray(u)

        if curr_x.ndim == 1:
            batch_mode = False
            # Concatenate state and input for a single sample
            x_aug = np.concatenate([curr_x, u])[np.newaxis, :]
        elif curr_x.ndim == 2:
            batch_mode = True
            # Concatenate state and input for a batch
            # If u is also 2D (batch_size, input_size)
            if u.ndim == 2:
                x_aug = np.concatenate([curr_x, u], axis=1)
            else:
                # If u is 1D, tile it or assume it's one input for all?
                # Usually in batch mode, u is also batched.
                u_batched = np.tile(u, (curr_x.shape[0], 1))
                x_aug = np.concatenate([curr_x, u_batched], axis=1)
        else:
            raise ValueError(f"curr_x must be 1D or 2D, got shape {curr_x.shape}")

        all_names = self.state_names + self.input_names
        n_cols = x_aug.shape[1]
        
        if n_cols == len(all_names):
            name_to_col = {name: i for i, name in enumerate(all_names)}
        elif n_cols == len(self.state_names):
            name_to_col = {name: i for i, name in enumerate(self.state_names)}
            x_aug = x_aug[:, :len(self.state_names)] # redundant but clear
        else:
            raise ValueError(
                f"Augmented state has {n_cols} columns, expected {len(self.state_names)} (states) "
                f"or {len(all_names)} (states+inputs)."
            )

        batch_size = x_aug.shape[0]
        predictions_cols = []

        for i, state_name in enumerate(self.state_names):
            try:
                predictor = self.predictors[state_name]
            except:
                # passthrough current state column i (batched)
                predictions_cols.append(x_aug[:, i].reshape(batch_size, 1))
                continue

            feature_names = predictor.get_feature_names()
            used_features = [f for f in feature_names if f in name_to_col]
            if len(used_features) != len(feature_names):
                missing = [f for f in feature_names if f not in name_to_col]
                raise ValueError(
                    f"Missing features for predictor '{state_name}': {missing}. "
                    f"Available columns: {list(name_to_col.keys())}"
                )

            feats = np.column_stack([x_aug[:, name_to_col[f]] for f in used_features])  # (batch_size, n_features)

            if hasattr(predictor, "predict_batch"):
                pred_vec = predictor.predict_batch(feats)  # (batch_size,)
            else:
                pred_vec = np.array([predictor.predict(row.tolist()) for row in feats], dtype=float)

            predictions_cols.append(pred_vec.reshape(batch_size, 1))

        out = np.concatenate(predictions_cols, axis=1)  # (batch_size, state_size)
        return out[0] if not batch_mode else out