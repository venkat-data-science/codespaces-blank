# client.py

import asyncio
import json
import websockets
import requests

CLIENT_ID = "client123"
SERVER_URL = "http://localhost:8000"
WS_URL = f"ws://localhost:8000/ws/{CLIENT_ID}"


# -----------------------------
# WebSocket Listener
# -----------------------------
async def listen_to_status():
    async with websockets.connect(WS_URL) as websocket:
        print("Connected to server...")

        # Keep connection alive
        asyncio.create_task(send_heartbeat(websocket))

        while True:
            message = await websocket.recv()
            data = json.loads(message)

            print(f"\nStage: {data['stage']}")
            print(f"Message: {data['message']}")
            print(f"Progress: {data['progress']}%")

            if data['stage'] == "completed":
                print("Processing completed. Disconnecting...")
                break


async def send_heartbeat(websocket):
    while True:
        await websocket.send("ping")
        await asyncio.sleep(10)


# -----------------------------
# Upload File
# -----------------------------
def upload_file():
    files = {"file": open("sample.pdf", "rb")}
    response = requests.post(f"{SERVER_URL}/upload/{CLIENT_ID}", files=files)
    print("Upload Response:", response.json())


# -----------------------------
# Main
# -----------------------------
async def main():
    # Start WebSocket listener
    listener_task = asyncio.create_task(listen_to_status())

    await asyncio.sleep(1)  # ensure websocket connected

    # Upload file
    upload_file()

    await listener_task


if __name__ == "__main__":
    asyncio.run(main())