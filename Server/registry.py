
"""
@author Henri-Welsch
@sources {
    https://charlesreid1.github.io/python-patterns-the-registry.html
    https://realpython.com/python-double-underscore/
    https://developers.home-assistant.io/docs/api/websocket/#subscribe-to-events
}
"""

class Registry:
    _registry = {}

    @classmethod
    def register(cls, name, obj):
        cls._registry[name] = obj

    @classmethod
    def get(cls, name):
        return cls._registry.get(name)

    @classmethod
    def get_snapshot(cls):
        return cls._registry.copy()

    @classmethod
    def get_system_states(cls, entity_ids):
        """
        Returns the current state of each entity_id in the provided list.

        Args:
            entity_ids (list of str): entity IDs to query

        Returns:
            list: states corresponding to each entity_id in order; None if not found
        """
        # Take a snapshot of the registry
        snapshot = cls.get_snapshot()
        states = []

        for entity_id in entity_ids:
            entry = snapshot.get(entity_id)
            if entry is not None:
                try:
                    state = entry["event"]["data"]["new_state"]["state"]
                except (KeyError, TypeError):
                    state = None
                states.append(float(state))
            else:
                states.append(None)

        return states