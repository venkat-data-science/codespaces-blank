# server.py

import asyncio
import json
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, BackgroundTasks

app = FastAPI()

# Store active websocket connections
active_connections: Dict[str, WebSocket] = {}


# -----------------------------
# WebSocket Endpoint
# -----------------------------
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    print(f"{client_id} connected")

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"{client_id} disconnected")
        active_connections.pop(client_id, None)


# -----------------------------
# Helper: Send Status
# -----------------------------
async def send_status(client_id: str, stage: str, message: str, progress: int = None):
    if client_id in active_connections:
        websocket = active_connections[client_id]

        payload = {
            "stage": stage,
            "message": message,
            "progress": progress
        }

        await websocket.send_text(json.dumps(payload))


# -----------------------------
# Background PDF + LLM Process
# -----------------------------
async def process_pdf(client_id: str, filename: str):

    await send_status(client_id, "file_uploaded", "File successfully uploaded")

    # Simulate PDF parsing
    await send_status(client_id, "parsing", "Parsing PDF...")
    await asyncio.sleep(2)

    total_pages = 20

    for page in range(1, total_pages + 1):
        await send_status(
            client_id,
            "llm_processing",
            f"Processing page {page} of {total_pages}",
            progress=int((page / total_pages) * 100)
        )

        # 🔥 Simulate long LLM call
        await asyncio.sleep(1)

    await send_status(client_id, "json_creation", "Generating final JSON...")
    await asyncio.sleep(2)

    await send_status(client_id, "completed", "Processing completed!", 100)


# -----------------------------
# File Upload Endpoint
# -----------------------------
@app.post("/upload/{client_id}")
async def upload_file(client_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...)):

    # Save file (simple example)
    file_location = f"./{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Start background processing
    background_tasks.add_task(process_pdf, client_id, file.filename)

    return {"message": "File received. Processing started."}