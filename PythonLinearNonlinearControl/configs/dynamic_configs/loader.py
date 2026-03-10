import json
from pathlib import Path

from .schema import RawConfig, StateConfig, ActionConfig


def load_raw_config(path: str | Path) -> RawConfig:
    data = json.loads(Path(path).read_text())

    # filter out unknown keys for ActionConfig
    action_data = data["action"].copy()
    action_keys = {f.name for f in ActionConfig.__dataclass_fields__.values()}
    filtered_action = {k: v for k, v in action_data.items() if k in action_keys}
    
    # Handle the "some good name" from the issue description if it exists
    # If the user provides a key that is not in our schema, we should probably 
    # check if it looks like discrete actions.
    # But for now, let's assume they might use 'discrete_actions' or we can map it.
    if "discrete_actions" not in filtered_action:
        # Check if there's any key that's a list of lists (excluding known ones)
        for k, v in action_data.items():
            if k not in action_keys and isinstance(v, list) and len(v) > 0 and isinstance(v[0], list):
                filtered_action["discrete_actions"] = v
                break

    return RawConfig(
        name=data.get("name", "UnnamedConfig"),
        type=data.get("type", "Nonlinear"),
        dt=float(data["dt"]),
        pred_len=int(data["pred_len"]),
        state=StateConfig(**data["state"]),
        action=ActionConfig(**filtered_action),
        opt_config=data.get("opt_config", {}),
    )