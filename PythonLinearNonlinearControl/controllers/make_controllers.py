from PythonLinearNonlinearControl.controllers.optimization_based_controllers.mpc import LinearMPC
from PythonLinearNonlinearControl.controllers.derivative_free_controllers.cem import CEM
from PythonLinearNonlinearControl.controllers.derivative_free_controllers.random import RandomShooting
from PythonLinearNonlinearControl.controllers.derivative_free_controllers.brute_force import BruteForce
from PythonLinearNonlinearControl.controllers.derivative_free_controllers.mppi import MPPI
from PythonLinearNonlinearControl.controllers.derivative_free_controllers.mppi_williams import MPPIWilliams
from PythonLinearNonlinearControl.controllers.gradient_based_controllers.ilqr import iLQR
from PythonLinearNonlinearControl.controllers.gradient_based_controllers.ddp import DDP
from PythonLinearNonlinearControl.controllers.gradient_based_controllers.nmpc import NMPC
from PythonLinearNonlinearControl.controllers.gradient_based_controllers.nmpc_cgmres import NMPCCGMRES


def make_controller(args, config, model):

    if args.controller_type == "MPC":
        return LinearMPC(config, model)
    elif args.controller_type == "CEM":
        return CEM(config, model)
    elif args.controller_type == "Random":
        return RandomShooting(config, model)
    elif args.controller_type == "BruteForce":
        return BruteForce(config, model)
    elif args.controller_type == "MPPI":
        return MPPI(config, model)
    elif args.controller_type == "MPPIWilliams":
        return MPPIWilliams(config, model)
    elif args.controller_type == "iLQR":
        return iLQR(config, model)
    elif args.controller_type == "DDP":
        return DDP(config, model)
    elif args.controller_type == "NMPC":
        return NMPC(config, model)
    elif args.controller_type == "NMPCCGMRES":
        return NMPCCGMRES(config, model)

    raise ValueError("No controller: {}".format(args.controller_type))
