from engines.tts_base import BaseTTSEngine
from kokoro import KPipeline, KModel
import torch
from utils.utils import find_device_available
import sounddevice as sd
SAMPLING_RATE = 24000
import logging


class KokoroTTS(BaseTTSEngine):
    def __init__(self, config=None):
        super().__init__(config)
        self.device =  find_device_available()
        #No support for mps device from kokoro
        if self.device == "mps":
            self.device = "cpu"

        self.initialize_model()
        self.voice = self.config.get('voice', 'af_heart') if self.config else 'af_heart'
        self.speed = 1
    


    def initialize_model(self):
        self.model = KModel(repo_id='hexgrad/Kokoro-82M').to(self.device).eval()
        self.pipeline = KPipeline(lang_code='a',model=False)
        self.pipeline.g2p.lexicon.golds['kokoro'] = 'kˈOkəɹO'
        logging.info("Loaded kokoro model and pipeline, ready to fire!")
        

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
        pack = self.pipeline.load_voice(self.voice)
        for _, ps, _ in self.pipeline(text, self.voice, self.speed, split_pattern=r'\n|\.+'):
            ref_s = pack[len(ps)-1]
            try:
                audio = self.model(ps, ref_s, self.speed)
                #return (24000, audio.to('cpu').squeeze().numpy()), ps
                yield audio.to('cpu').squeeze().numpy()
            except Exception as e:
                logging.error(f"Error converting {text} to audio {e}")
               
        # return None, ''


if __name__ == "__main__":
    k = KokoroTTS()
    k.convert_text_to_audio("Completely fooled by the innocent looking face on his shoulders and fell for his trick")


         

