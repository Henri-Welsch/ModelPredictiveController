from dataclasses import dataclass
from typing import Any


@dataclass
class StateConfig:
    names: list[str]
    goal: list[float]
    Q: list[float]
    Sf: list[float]


@dataclass
class ActionConfig:
    names: list[str]
    lower: list[float] = None
    upper: list[float] = None
    R: list[float] = None
    discrete_actions: list[list[float]] = None


@dataclass
class RawConfig:
    name: str
    type: str
    dt: float
    pred_len: int

    state: StateConfig
    action: ActionConfig

    opt_config: dict[str, Any]