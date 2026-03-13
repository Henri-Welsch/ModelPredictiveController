import os
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fastapi import FastAPI

from PythonLinearNonlinearControl.common.utils import load_xgboost_models_as
from PythonLinearNonlinearControl.configs.dynamic_configs.builder import build_control_config
from PythonLinearNonlinearControl.configs.dynamic_configs.loader import load_raw_config
from PythonLinearNonlinearControl.controllers.derivative_free_controllers.brute_force import BruteForce
from PythonLinearNonlinearControl.models.composite_models.greenhouse_composite_model import GreenhouseCompositeModel
from PythonLinearNonlinearControl.planners import ConstantPlanner
from PythonLinearNonlinearControl.runners.live_runner import LiveRunner
from Server.helpers import load_boosters
from Server.mpc_controller import MPCController
from client import Client

# Load environment variables
load_dotenv()

# Initialize the scheduler
scheduler = AsyncIOScheduler()


async def startup(app: FastAPI):
    """
    Startup routine for the FastAPI app.
    Sets up client, loads config, initializes controller and runner, and schedules periodic jobs.
    """
    # Initialize and connect client



    # Schedule runner to execute every 1 minutes
    mpc_controller = MPCController()

    app.state.client = Client(
        ws_url=os.getenv("HOME_ASSISTANT_WS_URL"),
        token=os.getenv("ACCESS_TOKEN"),
        mpc_controller=mpc_controller
    )
    await app.state.client.connect()

    # scheduler.add_job(mpc_controller.run, "interval", minutes=1)
    # scheduler.start()


async def shutdown(app: FastAPI):
    """
    Shutdown routine for the FastAPI app.
    Stops the scheduler and disconnects the client.
    """
    scheduler.shutdown()
    await app.state.client.disconnect()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager for managing the FastAPI app's lifespan.
    """
    await startup(app)
    yield
    await shutdown(app)


# Initialize FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    """
    Simple endpoint to verify server is running.
    """
    return {"message": "FastAPI server running!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=False)