from engines.tts_base import BaseTTSEngine
from kokoro import KPipeline, KModel
import torch
from utils.utils import find_device_available
import sounddevice as sd
SAMPLING_RATE = 24000

class KokoroTTS(BaseTTSEngine):
    def __init__(self, config=None):
         super().__init__(config)
         self.device =  find_device_available()
         self.model = self.initialize_model()
         

    def initialize_model(self):
        self.model = KModel().to(self.device).eval()
        self.pipeline = KPipeline(lang_code='a')

    def convert_text_to_audio(self,text):
        generator = self.pipeline(
            text, 
            voice='af_heart', 
            speed=1, 
            split_pattern=r'\n+'
        )
        #return generator
        for i, (_,_,audio) in enumerate(generator):
            speech = audio.to("cpu").squeeze().numpy()
            sd.play(speech, SAMPLING_RATE, blocking=True)
            # yield speech
    def stream_text_to_audio(self, text):
        #Lets first tokenize to phonemes



if __name__ == "__main__":
    k = KokoroTTS()
    k.convert_text_to_audio("Completely fooled by the innocent looking face on his shoulders and fell for his trick")


         

