import asyncio
import json
import os

import websockets

from Greiveldange.Server.registry import Registry
from Tools.custom_logger import logger

"""
@author Henri-Welsch
@sources {
    https://developers.home-assistant.io/docs/api/websocket/
    https://docs.python.org/3/library/asyncio.html
    https://websockets.readthedocs.io/en/stable/
}
"""

class Client:
    def __init__(self, ws_url: str, token: str):
        self.ws_url = ws_url
        self.token = token
        self.websocket = None
        self.connected = False

    async def connect(self):
        """Establish WebSocket connection and authenticate."""
        logger.info("Connecting to Home Assistant WebSocket, sending connection request...")
        self.websocket = await websockets.connect(self.ws_url)

        # Wait for auth_required
        initial_message = await self.websocket.recv()
        data = json.loads(initial_message)
        logger.info(f"Home Assistant response: {data}")

        if data.get("type") != "auth_required":
            logger.error("Unexpected message received during authentication: {data}")
            await self.websocket.close()

        # Authenticate and subscribe to events
        await self.authenticate()
        await self.subscribe_to_events()

        # Start listening for messages
        asyncio.create_task(self.listen())
        return self.connected


    async def authenticate(self):
        """Authenticate with Home Assistant using the token."""
        auth_message = {"type": "auth", "access_token": self.token}
        await self.websocket.send(json.dumps(auth_message))
        logger.info("Sent authentication token")

        auth_response = await self.websocket.recv()
        auth_data = json.loads(auth_response)
        logger.info(f"Home Assistant response: {auth_data}")

        if auth_data.get("type") != "auth_ok":
            logger.error("Authentication failed! Now closing WebSocket connection.")
            self.connected = False
            await self.websocket.close()


    async def subscribe_to_events(self):
        """Subscribe to state changes."""
        subscribe_message = {"id": 1, "type": "subscribe_events", "event_type": "state_changed"}
        await self.websocket.send(json.dumps(subscribe_message))
        logger.info("Sent subscription message")

        # Wait for subscription confirmation
        subscribe_response = await self.websocket.recv()
        subscribe_data = json.loads(subscribe_response)
        logger.info(f"Home Assistant response: {subscribe_data}")

        if subscribe_data.get("success") is not True:
            logger.error("Failed to subscribe to state changes! Now closing WebSocket connection.")
            self.connected = False
            await self.websocket.close()

        return subscribe_response


    async def listen(self):
        """Continuously listen for messages from Home Assistant."""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.ConnectionClosed:
            logger.warning("WebSocket connection closed.")


    @staticmethod
    async def handle_message(message: dict):
        """Process incoming messages."""
        # logger.info(f"Received message: {message}")

        if message.get("type") == "event":
            entity_id = message.get("event").get("data").get("entity_id")
            Registry.register(entity_id, message)
        else:
            logger.warning(f"Unknown message type: {message}")

# TODO: This is just for testing, remove later!
async def main():
    HOME_ASSISTANT_WS_URL = os.getenv("HOME_ASSISTANT_WS_URL")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    client = Client(HOME_ASSISTANT_WS_URL, ACCESS_TOKEN)
    await client.connect()

    # Keep the program running
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())