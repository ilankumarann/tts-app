import torch
import sounddevice as sd

class TacotranTTS():
    def __init__(self):
        self.tacotron2 = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_tacotron2', model_math='fp16')
        self.tacotron2 = self.tacotron2.to('cuda')
        self.tacotron2.eval()

        self.waveglow = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_waveglow', model_math='fp16')
        self.waveglow = self.waveglow.remove_weightnorm(self.waveglow)
        self.waveglow = self.waveglow.to('cuda')
        self.waveglow.eval()

        self.utils = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_tts_utils')

    def speak(self, text):
        sequences, lengths = self.utils.prepare_input_sequence([text])

        with torch.no_grad():
            mel, _, _ = self.tacotron2.infer(sequences, lengths)
            audio = self.waveglow.infer(mel)
        audio_numpy = audio[0].data.cpu().numpy()
        rate = 22050
        sd.play(audio_numpy, rate)
        sd.wait()