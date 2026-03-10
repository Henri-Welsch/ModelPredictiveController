import argparse

from PythonLinearNonlinearControl.common.utils import load_xgboost_models_as
from PythonLinearNonlinearControl.configs.dynamic_configs.builder import build_control_config
from PythonLinearNonlinearControl.configs.dynamic_configs.loader import load_raw_config
from PythonLinearNonlinearControl.controllers.derivative_free_controllers.brute_force import BruteForce
from PythonLinearNonlinearControl.helper import bool_flag, make_logger
from PythonLinearNonlinearControl.controllers.make_controllers import make_controller
from PythonLinearNonlinearControl.models.composite_models.greenhouse_composite_model import GreenhouseCompositeModel
from PythonLinearNonlinearControl.planners import ConstantPlanner
from PythonLinearNonlinearControl.planners.make_planners import make_planner
from PythonLinearNonlinearControl.configs.make_configs import make_config
from PythonLinearNonlinearControl.models.make_models import make_model
from PythonLinearNonlinearControl.envs.make_envs import make_env
from PythonLinearNonlinearControl.runners.live_runner import LiveRunner
from PythonLinearNonlinearControl.runners.make_runners import make_runner
from PythonLinearNonlinearControl.plotters.plot_func import plot_results, \
    save_plot_data
from PythonLinearNonlinearControl.plotters.animator import Animator


def run(config, predictors):
    planner = ConstantPlanner(config)
    model = GreenhouseCompositeModel(predictors, config)
    controller = BruteForce(config, model)
    runner = LiveRunner(controller, planner)

    u = runner.run(config.curr_state, config.goal_state)

    print("u: {}".format(u))


def main():
    raw = load_raw_config("C:/Users/WelJo/IdeaProjects/test/PythonLinearNonlinearControl/configs/dynamic_configs/configs/rita.json")
    predictors = load_xgboost_models_as("C:/Users/WelJo/Desktop/modelTest")
    config = build_control_config(raw)

    run(config, predictors)


if __name__ == "__main__":
    main()
