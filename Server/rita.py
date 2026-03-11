from Greiveldange.PythonLinearNonlinearControl.environment.rita_environments import RitaEnvironment
from Greiveldange.PythonLinearNonlinearControl.models.base_model import Model
from Greiveldange.PythonLinearNonlinearControl.models.rita_model import RitaModel, XGBoostPredictorAdapter
from Greiveldange.PythonLinearNonlinearControl.planners.base_planner import Planner
from Greiveldange.PythonLinearNonlinearControl.planners.constant_planner import ConstantPlanner
from Greiveldange.PythonLinearNonlinearControl.runners.runner import ExpRunner
from Greiveldange.PythonLinearNonlinearControl.controllers.base_controller import Controller
from Greiveldange.PythonLinearNonlinearControl.controllers.random_shooting_controller import RandomShootingController
from Greiveldange.PythonLinearNonlinearControl.environment.base_environment import Environment
from Greiveldange.Server.registry import Registry


class Rita:

    def __init__(self, greenhouse_configuration: dict, booster_models: list):
        environment: Environment = RitaEnvironment(greenhouse_configuration)
        planner: Planner = ConstantPlanner(environment)
        # Wrap each XGBoost model in an adapter
        predictors = [XGBoostPredictorAdapter(m) for m in booster_models]
        model: Model = RitaModel(predictors)
        controller: Controller = RandomShootingController(environment, model)
        self.runner = ExpRunner(environment, controller, planner)

        self.goal_state_feature_names = greenhouse_configuration.get("goal_state_feature_names")
        self.input_feature_names = greenhouse_configuration.get("input_feature_names")
        self.greenhouse_configuration = greenhouse_configuration

    async def run(self):
        curr_x: list[float] = Registry.get_system_states(self.goal_state_feature_names)
        goal_x = self.greenhouse_configuration.get("goal_state")

        if self.goal_state_feature_names:
            print(f"Goal state features: {self.goal_state_feature_names}")
        if self.input_feature_names:
            print(f"Input features: {self.input_feature_names}")

        history_x, history_u, history_g = self.runner.run(curr_x, goal_x)
        print(history_x, history_u, history_g)
