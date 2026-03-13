import asyncio
import json
import os

import websockets
from dotenv import load_dotenv

from Server.custom_logger import setup_custom_logger
from Server.registry import Registry

import logging
logger = logging.getLogger(__name__)

class Client:
    """
    Class for testing Home Assistant WebSocket API client functionality.

    auther: Henri-Welsch
    references:
        https://developers.home-assistant.io/docs/api/websocket/
        https://github.com/music-assistant/python-hass-client/blob/main/hass_client/client.py
    """

    def __init__(self, websocket_url, token):
        self._websocket_url = websocket_url
        self._token = token
        self._websocket = None
        self._result_futures = {}
        self._message_id = 0


    async def connect(self):
        # Connection to Home Assistant API and sending an authentication message.
        # https://developers.home-assistant.io/docs/api/websocket/#authentication-phase
        logger_message = "Connecting to Home Assistant Websocket API on %s"
        logger.info(logger_message, self._websocket_url)

        try:
            self._websocket = await websockets.connect(self._websocket_url)
            response_raw = await self._websocket.recv()
            logger.info("Response from Home Assistant: %s", response_raw)

            await self._authenticate()
            asyncio.create_task(self._traffic_handler())
        except asyncio.TimeoutError:
            logger.error("Connection to Home Assistant timed out")
        except OSError:
            logger.error("Failed to connect to Home Assistant WebSocket API")
            await self.disconnect()


    async def _authenticate(self):
        # Send an authentication message to Home Assistant
        # https://developers.home-assistant.io/docs/api/websocket/#authentication-phase
        message: dict = {"type": "auth", "access_token": self._token}
        logger.info("Requesting authentication: %s", json.dumps(message))

        await self._websocket.send(json.dumps(message))
        response_raw: str = await self._websocket.recv()
        response: dict = json.loads(response_raw)
        logger.info("Response from Home Assistant: %s", response)

        if response.get("type") != "auth_ok":
            raise Exception("Authentication failed")


    async def disconnect(self):
        # Close the connection to the Home Assistant WebSocket API
        logger.debug("Closing Home Assistant Websocket API connection")
        await self._websocket.close()


    async def fetch_states(self):
        # Fetch the current state of all entities from Home Assistant
        # https://developers.home-assistant.io/docs/api/websocket/#fetching-states
        message_id: int = await self._get_message_id()
        message: dict = {"id": message_id, "type": "get_states"}
        logger.info("Requesting initial system state: %s", json.dumps(message))

        future = asyncio.get_running_loop().create_future()
        self._result_futures[message_id] = future
        await self._websocket.send(json.dumps(message))

        response: dict = await future
        Registry.initiate(response["result"])

        response["result"] = str(len(response.get("result"))) + " entities"
        logger.info("Response from Home Assistant: %s ", response)


    async def subscribe_to_events(self):
        # Subscribe to events / state changes from Home Assistant
        # https://developers.home-assistant.io/docs/api/websocket/#subscribe-to-events
        message_id: int = await self._get_message_id()
        message: dict = {"id": message_id, "type": "subscribe_events", "event_type": "state_changed"}
        logger.info("Requesting to subscribe to state changes: %s", json.dumps(message))

        future = asyncio.get_running_loop().create_future()
        self._result_futures[message_id] = future
        await self._websocket.send(json.dumps(message))

        response: dict = await future
        logger.info("Response from Home Assistant: %s", response)


    async def _traffic_handler(self):
        # Continuously read messages from the Home Assistant WebSocket API
        # This loop is used to handle multiple requests and responses
        # https://docs.python.org/3/library/asyncio-future.html
        try:
            while True:
                message_raw: str = await self._websocket.recv()
                message: dict = json.loads(message_raw)
                message_id: int = message.get("id")

                if message_id in self._result_futures:
                    logger.debug("Received message from Home Assistant: %s", message)
                    self._result_futures.pop(message_id).set_result(message)
                else:
                    state = message.get("event").get("data").get("new_state")
                    Registry.register(state.get("entity_id"), state)
        except websockets.ConnectionClosed:
            logger.warning("WebSocket connection closed")

    async def _get_message_id(self):
        self._message_id += 1
        return self._message_id






# TODO: This is just for testing, remove later!
async def main():
    load_dotenv()
    home_assistant_ws_url = os.getenv("HOME_ASSISTANT_WS_URL")
    access_token = os.getenv("ACCESS_TOKEN")

    client = Client(home_assistant_ws_url, access_token)
    await client.connect()
    await client.fetch_states()
    await client.subscribe_to_events()
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())