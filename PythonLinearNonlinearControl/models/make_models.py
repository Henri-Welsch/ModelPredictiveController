from PythonLinearNonlinearControl.models.experimental_models.first_order_lag import FirstOrderLagModel
from PythonLinearNonlinearControl.models.experimental_models.two_wheeled import TwoWheeledModel
from PythonLinearNonlinearControl.models.experimental_models.cartpole import CartPoleModel
from PythonLinearNonlinearControl.models.experimental_models.nonlinear_sample_system import NonlinearSampleSystemModel


def make_model(args, config):

    if args.env == "FirstOrderLag":
        return FirstOrderLagModel(config)
    elif args.env == "TwoWheeledConst" or args.env == "TwoWheeledTrack":
        return TwoWheeledModel(config)
    elif args.env == "CartPole":
        return CartPoleModel(config)
    elif args.env == "NonlinearSample":
        return NonlinearSampleSystemModel(config)

    raise NotImplementedError("There is not {} Model".format(args.env))
