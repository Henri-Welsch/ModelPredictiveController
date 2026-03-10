from logging import getLogger

import numpy as np

logger = getLogger(__name__)


class LiveRunner():
    """ live runner
    """

    def __init__(self, controller, planner):
        self.controller = controller
        self.planner = planner

    def run(self, curr_x, goal_x):
        g_xs = self.planner.plan(curr_x, goal_x)
        u = self.controller.obtain_sol(curr_x, g_xs)

        message = "Controller = {}, Goal = {}, Actions = {}"
        logger.debug(message.format(self.controller, goal_x, u))

        return u
