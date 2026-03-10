from dataclasses import dataclass
import numpy as np
from typing import Any


@dataclass(frozen=True)
class ControlConfig:
    name: str
    dt: float
    PRED_LEN: int

    state_names: list[str]
    action_names: list[str]

    STATE_SIZE: int
    INPUT_SIZE: int

    goal_state: np.ndarray

    Q: np.ndarray
    Sf: np.ndarray
    R: np.ndarray

    opt_config: dict[str, Any]

    INPUT_LOWER_BOUND: np.ndarray = None
    INPUT_UPPER_BOUND: np.ndarray = None
    
    DISCRETE_ACTIONS: list[np.ndarray] = None

    # ----- cost functions -----

    def input_cost_fn(self, u: np.ndarray) -> np.ndarray:
        return (u ** 2) * np.diag(self.R)

    def state_cost_fn(self, x: np.ndarray, g_x: np.ndarray) -> np.ndarray:
        return ((x - g_x) ** 2) * np.diag(self.Q)

    def terminal_state_cost_fn(self, x: np.ndarray, g: np.ndarray) -> np.ndarray:
        return ((x - g) ** 2) * np.diag(self.Sf)