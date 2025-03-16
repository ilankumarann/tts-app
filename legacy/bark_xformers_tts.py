# from transformers import BarkModel, BarkProcessor
# self.model = BarkModel.from_pretrained("suno/bark-small").to(self.device)
# self.processor = BarkProcessor.from_pretrained("suno/bark-small")
from transformers import BarkModel, AutoProcessor, BarkProcessor


import sounddevice as sd
import torch
from utils.utils import find_device_available 
import os
os.environ["SUNO_OFFLOAD_CPU"] = "True"
os.environ["SUNO_USE_SMALL_MODELS"] = "True"

class BarkTTS():
    def __init__(self):
        self.device = find_device_available()
        self.model = BarkModel.from_pretrained("suno/bark-small", torch_dtype=torch.float16).to(self.device)
        self.model.enable_cpu_offload()
        self.processor = AutoProcessor.from_pretrained("suno/bark-small")
        self.sampling_rate = self.model.generation_config.sample_rate


    def speak(self, text):
        # add a speaker embedding
        inputs = self.processor(text, return_tensors="pt", voice_preset="v2/en_speaker_1")
        inputs = inputs.to(self.device)
        speech_output = self.model.generate(**inputs, do_sample=True)
        speech_output = speech_output.to("cpu")  # Move the output to CPU for playback
        sd.play(speech_output.squeeze().to(torch.float32).numpy(), samplerate=self.sampling_rate)
        sd.wait()


    
    
    
            
# Example usage:
if __name__ == "__main__":
    tts = BarkTTS()
    tts.speak("Fine trained model can fuck up the output")