import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
from tts_engine import TTSEngine
import logging
import coloredlogs
from fastapi.staticfiles import StaticFiles
import sounddevice as sd

logger = logging.getLogger("Throatpain")
log_format = "%(levelname)s:%(asctime)s:%(name)s: %(message)s"
coloredlogs.install(level='DEBUG', logger=logger, fmt=log_format)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global tts_engine
    tts_engine = TTSEngine(backend_name="speecht5")
    yield
    tts_engine = None

app = FastAPI(lifespan=lifespan)
app.mount("/html", StaticFiles(directory="public"), name="static")

@app.get("/api/backends")
async def backends():
    backends = tts_engine.get_available_backends()
    return JSONResponse(backends)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            input = await websocket.receive_json()
            text = input.get("text", None)
            if text:
                audio,sr = tts_engine.convert_text_to_audio(text)
                audio_base64 = base64.b64encode(audio).decode('utf-8')
                response = {
                    "text": text,
                    "samplingRate" : sr,
                    "audio": audio_base64,
                    "numChannels" : 1,
                }
                await websocket.send_json(response)
               
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected")