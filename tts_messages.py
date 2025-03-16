from dataclasses import dataclass

@dataclass
class TTSRequest:
    session_id: str
    text: str

@dataclass
class TTSResponse:
    session_id: str
    audio: bytes