import os
import uvicorn
import asyncio

import xgboost
from dotenv import load_dotenv
from fastapi import FastAPI

from Greiveldange.PythonLinearNonlinearControl.helper import load_xgboost_models
from Greiveldange.Server.rita import Rita

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from PythonLinearNonlinearControl.models.composite_models.predictors.base_predictor import Predictor
from PythonLinearNonlinearControl.models.composite_models.predictors.xgboost_predictor import XGBoostPredictor
from client import Client

from Tools.json_reader import read

app = FastAPI()
load_dotenv()
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def establish_connection():
    """
    Establishes a connection to the Home Assistant WebSocket API upon application
    startup. This asynchronous function initializes a WebSocket client and launches
    a task to establish a persistent connection using provided credentials.

    :return: None
    """
    client = Client(os.getenv("HOME_ASSISTANT_WS_URL"), os.getenv("ACCESS_TOKEN"))
    asyncio.create_task(client.connect())


@app.on_event("startup")
async def start_services():
    """
    Performs initialization and starts services upon application startup. This function reads
    configuration files, loads machine learning models, initializes the greenhouse controller
    with provided configurations, and schedules recurring tasks using a job scheduler.

    :raises FileNotFoundError: If configuration file or model files are missing.
    :raises ValueError: If the configuration or models are invalid.
    """
    greenhouse_configuration: dict = read(os.getenv("GREENHOUSE_CONFIG_PATH"))
    booster_models: list = load_xgboost_models(os.getenv("BOOSTER_MODELS_PATH"))
    greenhouse: Rita = Rita(greenhouse_configuration, booster_models)

    scheduler.add_job(greenhouse.run,IntervalTrigger(seconds=30),id="my_task",replace_existing=True)
    scheduler.start()



@app.get("/")
def root():
    """
    To check if the server is running and reachable under 127.0.0.1:8000.
    """
    return {"message": "FastAPI server running!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=False)




def load_xgboost_models_as(folder_path: str) -> dict[str, Predictor]:
    """
    Load all XGBoost models from a folder and return Predictor-interface adapters keyed by filename.

    Returns:
        dict[str, SingleTargetPredictor]: { "<filename>.json": XGBoostPredictorAdapter(...) }
    """
    model_files_in_direcotory = os.listdir(folder_path)
    model_files = sorted([
        f for f in os.listdir(folder_path)
        if f.endswith(".json")
    ])

    predictors: dict[str, Predictor] = {}
    for filename in model_files:
        full_path = os.path.join(folder_path, filename)
        model = xgboost.XGBRegressor()
        model.load_model(full_path)

        predictor = XGBoostPredictor(model.get_booster())
        predictor_name = filename.replace(".json", "")
        predictors[predictor_name] = predictor

    return predictors