from bark import SAMPLE_RATE, generate_audio, preload_models
import os
import torch
os.environ["SUNO_OFFLOAD_CPU"] = "True"
os.environ["SUNO_USE_SMALL_MODELS"] = "True"
import sounddevice as sd

class BarkTTS():
    def __init__(self):
        preload_models()
        self.sampling_rate = SAMPLE_RATE

    def speak(self, text):
        speech_output = generate_audio(text, history_prompt="v2/en_speaker_1")
        sd.play(speech_output, samplerate=self.sampling_rate)
        sd.wait()



# Example usage:
if __name__ == "__main__":
    tts = BarkTTS()
    tts.speak("Fine trained model can fuck up the output")