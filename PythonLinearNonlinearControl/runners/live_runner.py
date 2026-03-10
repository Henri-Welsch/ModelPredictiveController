from logging import getLogger

import numpy as np

logger = getLogger(__name__)


class LiveRunner():
    """ live runner
    """

    def __init__(self):
        """
        """
        pass

    def run(self, controller, planner, curr_x, goal_x):
        """
        Returns:
            history_x (numpy.ndarray): history of the state,
            shape(episode length, state_size)
            history_u (numpy.ndarray): history of the state,
            shape(episode length, input_size)
        """
        # plan
        g_xs = planner.plan(curr_x, goal_x)

        # obtain sol
        u = controller.obtain_sol(curr_x, g_xs)

        message = "Controller = {}, Goal = {}, Actions = {}"
        logger.debug(message.format(controller, goal_x, u))
        return u
