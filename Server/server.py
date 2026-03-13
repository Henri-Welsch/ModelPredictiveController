import asyncio
import os
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from Server.client import Client
from Server.logging_config import setup_logging, LOGGING
from Server.mpc_controller import MPCController

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


class HomeAssistantServer:
    """
    Class-based FastAPI server managing the Home Assistant client lifecycle.
    """

    def __init__(self):
        self.running = None
        self.client = Client(os.getenv("HOME_ASSISTANT_WS_URL"), os.getenv("ACCESS_TOKEN"))
        self.controller = MPCController()
        self.app = FastAPI(lifespan=self.lifespan)

    async def websocket_startup(self):
        logger.info("Starting Home Assistant client...")
        await self.client.connect()
        await self.client.fetch_states()
        await self.client.subscribe_to_events()
        logger.info("Home Assistant client started successfully.")

    async def websocket_shutdown(self):
        logger.info("Disconnecting Home Assistant client...")
        await self.client.disconnect()
        logger.info("Home Assistant client disconnected.")

    async def mpc_startup(self):
        logger.info("Starting MPC system...")
        scheduler.add_job(self.safe_run, "interval", minutes=2)
        scheduler.start()
        logger.info("MPC system started successfully.")

    async def safe_run(self):
        if self.running:
            logger.warning("Previous MPC job still running, skipping this interval")
            return
        self.running = True
        try:
            result = await asyncio.to_thread(self.controller.run)
            await self.handle_result(result)
        finally:
            self.running = False

    async def handle_result(self, result):
        # Do something with the result, e.g., send actions to Home Assistant
        logger.info(f"Applying MPC action: {result}")


    async def mpc_shutdown(self):
        logger.info("Stopping MPC system...")
        scheduler.shutdown(wait=False)
        logger.info("MPC system stopped successfully.")


    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """
        Async context manager for managing the client lifecycle.
        """
        await self.websocket_startup()
        await self.mpc_startup()

        try:
            yield
        finally:
            await self.websocket_shutdown()
            await self.mpc_shutdown()


    def run(self, host="0.0.0.0", port=8000, reload=False):
        """
        Run the FastAPI app with Uvicorn.
        """
        uvicorn.run(self.app, host=host, port=port, reload=reload, log_config=LOGGING)


if __name__ == "__main__":
    server = HomeAssistantServer()
    server.run()