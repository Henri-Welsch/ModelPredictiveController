import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from Server.client import Client
from Server.custom_logger import setup_custom_logger
from Server.logging_config import setup_logging, LOGGING

import logging
logger = logging.getLogger(__name__)

load_dotenv()
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager for managing the FastAPI app's lifespan.
    """
    client = Client(os.getenv("HOME_ASSISTANT_WS_URL"), os.getenv("ACCESS_TOKEN"))
    await client.connect()
    await client.fetch_states()
    await client.subscribe_to_events()
    yield
    await client.disconnect()

app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False, log_config=LOGGING)