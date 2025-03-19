from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
from datasets import load_dataset

from engines.tts_base import BaseTTSEngine
from utils.utils import find_device_available
import logging

SAMPLING_RATE = 16000

class SpeechT5Backend(BaseTTSEngine):
    def __init__(self, config: dict=None):
        super().__init__(config)
        self.device = find_device_available()
        logging.info(f"MS TTS Engine using device {self.device}")
        self.processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        self.model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(self.device)
        self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan").to(self.device)
        self.embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        logging.info(f"MS TTS Engine - Models are loaded and ready to process requests")

    def convert_text_to_audio(self, text: str):
        inputs = self.processor(text=text, return_tensors="pt", normalize=True)
        inputs = inputs.to(self.device)
        speaker_embeddings = torch.tensor(self.embeddings_dataset[7306]["xvector"]).unsqueeze(0)
        speaker_embeddings = speaker_embeddings.to(self.device)
        speech = self.model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=self.vocoder)
        speech = speech.to("cpu").squeeze().numpy()
        return speech
    
    def stream_text_to_audio(text):
        raise NotImplementedError("Speect5 doesnt support streaming yet")