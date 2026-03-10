from dataclasses import dataclass


@dataclass
class StateConfig:
    names: list[str]
    goal: list[float]
    curr_x: list[float]

    Q: list[float]
    Sf: list[float]


@dataclass
class ActionConfig:
    names: list[str]
    discrete_actions: list[list[float]]
    R: list[float]


@dataclass
class RawConfig:
    name: str
    type: str
    dt: float
    pred_len: int

    state: StateConfig
    action: ActionConfig