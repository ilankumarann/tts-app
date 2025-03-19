import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from tts_engine import TTSEngine
import logging
import coloredlogs
from fastapi.staticfiles import StaticFiles
# import sounddevice as sd
from datetime import datetime
from types import GeneratorType
import uvicorn

logger = logging.getLogger("TTS Demo App")
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
    tts_engine = TTSEngine(backend_name="kokoro")
    yield
    tts_engine = None

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="public"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/backends")
async def backends():
    backends = tts_engine.get_available_backends()
    return JSONResponse(backends)

def prepare_audio_response(audio, sample_rate, num_channels, text, session_id=None):
    audio_base64 = base64.b64encode(audio).decode('utf-8')
    return  {
        "text": text,
        "samplingRate" : sample_rate,
        "audio": audio_base64,
        "numChannels" : num_channels,
        "sessionId" : session_id
    }  

async def handle_message(websocket:WebSocket, input:str|dict):
    if not input:
        return
    text = None
    session_id = None
    if isinstance(input, dict):
        text = input.get("text", None)
        session_id = input.get("session_id", None)
    elif isinstance(input, str):
        text = input
        session_id = None
    
    if text:
        logging.debug(f"Converting text {text}")
        st = datetime.now()
        result = tts_engine.convert_text_to_audio(text)
        dt = datetime.now()
        if isinstance(result, GeneratorType):
            if tts_engine.backend_name == "kokoro":
                for audio_bytes in result:
                    await websocket.send_json(
                        prepare_audio_response(audio_bytes,tts_engine.sampling_rate, 1, text, session_id=session_id)
                    )
            elif tts_engine.backend_name == "parler":
                logger.info("Parler not yet implemented")
            else:
                logger.info(f"Unsupported backend {tts_engine.backend_name} for streaming")
        else:
            await websocket.send_json(
                prepare_audio_response(result,tts_engine.sampling_rate, 1, text, session_id=session_id)
            )
        dt = datetime.now()
        logger.debug(f" Took {dt - st} to convert to audio") 
    
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            input = await websocket.receive_json()
            try:
                await handle_message(websocket,input)
            except Exception as e:
                logger.error(f"Error in converting audio, {str(e)}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected")
    

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8000)      