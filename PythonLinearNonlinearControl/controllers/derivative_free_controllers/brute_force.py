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
        # we expect a step size or number of divisions for each input dimension
        self.step_size = config.opt_config.get("BruteForce", {}).get("step_size", 0.1)

        # get bound
        self.input_upper_bounds = config.INPUT_UPPER_BOUND
        self.input_lower_bounds = config.INPUT_LOWER_BOUND

        # generate all possible inputs for one time step
        # TODO: Change from continues to discrete
        self.possible_inputs_per_step = []
        for i in range(self.input_size):
            low = self.input_lower_bounds[i]
            high = self.input_upper_bounds[i]
            # create range of values for each input dimension
            # Ensure we include both lower and upper bounds if possible
            num_steps = int(np.ceil((high - low) / self.step_size)) + 1
            vals = np.linspace(low, high, num_steps)
            self.possible_inputs_per_step.append(vals)

        # All combinations for a single time step
        # shape (num_combos_per_step, input_size)
        self.single_step_combos = np.array(list(itertools.product(*self.possible_inputs_per_step)))

        # All combinations for the entire prediction horizon
        # This will be HUGE if pred_len is large!
        # shape (num_combos_per_step^pred_len, pred_len, input_size)
        
        # itertools.product(*[self.single_step_combos] * self.pred_len)
        # However, to use calc_cost, we need (pop_size, pred_len, input_size)
        
        # We'll generate this on the fly or pre-calculate if memory allows.
        # For small systems as requested, this should be okay.
        
        all_combos_gen = itertools.product(self.single_step_combos, repeat=self.pred_len)
        self.samples = np.array(list(all_combos_gen))
        self.pop_size = self.samples.shape[0]

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
        # calc cost
        costs = self.calc_cost(curr_x, self.samples, g_xs)

        # solution
        sol = self.samples[np.argmin(costs)]

        return sol[0]

    def __str__(self):
        return "BruteForce"
