import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from listener import GT7Communication
from lap import Lap
import json

app = FastAPI()

gt7_instances = {}

@app.websocket("/ws/telemetry")
async def telemetry_ws(websocket: WebSocket, ip: str = Query(...)):
    await websocket.accept()
    if ip not in gt7_instances:
        gt7_comm = GT7Communication(ip)
        gt7_comm.current_lap = Lap()
        gt7_comm.start()
        gt7_instances[ip] = gt7_comm
    else:
        gt7_comm = gt7_instances[ip]
    
    try:
        while True:
            data = gt7_comm.get_last_data()
            if data is not None and hasattr(data, "to_dict"):
                # Serialization of JSON data
                await websocket.send_text(json.dumps(data.to_dict()))
            await asyncio.sleep(0.05)
    except WebSocketDisconnect: print(f"Client disconnected from {ip}")
    except Exception as e: print(f"WebSocket error: {e}")