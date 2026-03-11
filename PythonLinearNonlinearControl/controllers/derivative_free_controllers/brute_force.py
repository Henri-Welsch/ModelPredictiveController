from logging import getLogger
import itertools

import numpy as np

from PythonLinearNonlinearControl.controllers.controller import Controller

logger = getLogger(__name__)


class BruteForce(Controller):
    """ Brute Force Method for linear and nonlinear method

    Attributes:
        history_u (list[numpy.ndarray]): time history of optimal input
    """

    def __init__(self, config, model):
        super(BruteForce, self).__init__(config, model)

        # model
        self.model = model

        # general parameters
        self.pred_len = config.PRED_LEN
        self.input_size = config.INPUT_SIZE

        # brute force parameters
        # No parameters to set

        # get bound
        self.discrete_actions = config.DISCRETE_ACTIONS

        # generate all possible inputs for one time step
        self.possible_inputs_per_step = self.discrete_actions

        # get cost func
        self.state_cost_fn = config.state_cost_fn
        self.terminal_state_cost_fn = config.terminal_state_cost_fn
        self.input_cost_fn = config.input_cost_fn

        # save
        self.history_u = []

    def obtain_sol(self, curr_x, g_xs):
        """ calculate the optimal inputs

        Args:
            curr_x (numpy.ndarray): current state, shape(state_size, )
            g_xs (numpy.ndarrya): goal trajectory, shape(plan_len, state_size)
        Returns:
            opt_input (numpy.ndarray): optimal input, shape(input_size, )
        """
        # generate all possible inputs for a single time step
        single_step_combos = np.array(list(itertools.product(*self.possible_inputs_per_step)))

        # generate all possible inputs for all time steps
        samples = np.array(list(itertools.product(single_step_combos, repeat=self.pred_len)))

        # calc cost
        costs = self.calc_cost(curr_x, samples, g_xs)

        # solution
        sol = samples[np.argmin(costs)]

        return sol[0]

    def __str__(self):
        return "BruteForce"
