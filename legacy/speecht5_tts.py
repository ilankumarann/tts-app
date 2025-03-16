import re
from dateparser.search import search_dates
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import sounddevice as sd
import torch
from datasets import load_dataset
from utils.utils import date_time_to_tokens, find_device_available, split_acronyms
from scipy.io.wavfile import write  # Import the write function from scipy.io.wavfile
from queue import Queue
from queue import Empty
from threading import Thread, Event


class SpeechT5TTS():
    def __init__(self, iq:Queue=None):
        self.terminate = Event()
        self.input_queue = iq
        self.device = find_device_available()
        # self.device = "cpu"
        self.processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        self.model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(self.device)
        self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan").to(self.device)
        self.embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        self.t = Thread(target=self.listen_queue)

    def convert(self, text):
        inputs = self.processor(text=text, return_tensors="pt", normalize=True)
        inputs = inputs.to(self.device)
        speaker_embeddings = torch.tensor(self.embeddings_dataset[7306]["xvector"]).unsqueeze(0)
        speaker_embeddings = speaker_embeddings.to(self.device)
        speech = self.model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=self.vocoder)
        return speech.to("cpu").squeeze().numpy()

    def play(self, speech):    
        # Play the generated speech
        sd.play(speech, samplerate=16000)
        sd.wait()  # Wait until the speech is done playing

    def save_to_wav(self, speech, filename):
        # Save the generated speech to a WAV file
        write(filename, 16000, speech)

    def speak(self, text):
        text = self.input_pre_processor(text)
        speech = self.convert(text)
        self.play(speech)
        # self.save_to_wav(speech, "output.wav")  # Save the speech to a WAV file

    def input_pre_processor(self, text):
        """
        Pre-process the input text before passing it to the model
        identifies the date and time and converts it to a readable format
        also changes the symbol & to and
        """
        text = text.replace("&", " and ")
        text = split_acronyms(text)
        # dates = search_dates(text)
        # for d in dates:
        #     text = text.replace(d[0], date_time_to_tokens(d[1]))
        # Add a blank token to the text
        text  = " " + text + " "
        return text

    def listen_queue(self):
        if self.input_queue is None:
            raise ValueError("Input queue is not set")
        while not self.terminate.is_set():
            try:
                text = self.input_queue.get(timeout=0.1)
                if text:
                    self.speak(text)
                    self.input_queue.task_done()
            except Empty:
                pass
    
    def stop(self):
        self.terminate.set()
        self.t.join()

# # Example usage:
# if __name__ == "__main__":
#     tts = SpeechT5TTS()
#     tts.speak("\t Hello, Champions trophy final is on seventh March 2025")