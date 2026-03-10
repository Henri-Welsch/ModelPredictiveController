from .experimental_runner import ExpRunner
from .live_runner import LiveRunner


def make_runner(args):
    if args.runner_type == "experimental":
        return ExpRunner()
    elif args.runner_type == "live":
        return LiveRunner()

    raise ValueError(f"Invalid runner type: {args.runner_type}")
