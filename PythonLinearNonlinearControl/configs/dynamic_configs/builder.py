import numpy as np

from .schema import RawConfig
from .runtime import ControlConfig


def build_control_config(raw: RawConfig) -> ControlConfig:

    state_names = raw.state.names
    action_names = raw.action.names

    goal = np.array(raw.state.goal, dtype=float)

    Q = np.diag(raw.state.Q)
    Sf = np.diag(raw.state.Sf)
    R = np.diag(raw.action.R)

    lower = np.array(raw.action.lower, dtype=float) if raw.action.lower is not None else None
    upper = np.array(raw.action.upper, dtype=float) if raw.action.upper is not None else None

    discrete_actions = [np.array(a, dtype=float) for a in raw.action.discrete_actions] if raw.action.discrete_actions is not None else None

    # validation
    if len(state_names) != goal.shape[0]:
        raise ValueError("state names and goal mismatch")

    if discrete_actions is not None:
        if len(action_names) != len(discrete_actions):
            raise ValueError("action names and discrete actions mismatch")
    elif lower is not None:
        if len(action_names) != lower.shape[0]:
            raise ValueError("action bounds mismatch")
    else:
        raise ValueError("Either lower/upper bounds or discrete actions must be defined")

    return ControlConfig(
        name=raw.name,
        dt=raw.dt,
        PRED_LEN=raw.pred_len,

        state_names=state_names,
        action_names=action_names,

        STATE_SIZE=len(state_names),
        INPUT_SIZE=len(action_names),

        goal_state=goal,

        Q=Q,
        Sf=Sf,
        R=R,

        opt_config=raw.opt_config,

        INPUT_LOWER_BOUND=lower,
        INPUT_UPPER_BOUND=upper,
        DISCRETE_ACTIONS=discrete_actions,
    )