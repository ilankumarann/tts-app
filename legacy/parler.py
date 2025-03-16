import torch
from parler_tts import ParlerTTSForConditionalGeneration, ParlerTTSStreamer
from transformers import AutoTokenizer
#import soundfile as sf
import sounddevice as sd
from datetime import datetime
from threading import Thread, Event
import queue

class ParlerTTS():
    def __init__(self, input_quque=None):
        self.input_queue = input_quque
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.torch_type = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        self.max_len = 50
        self.attn = "flash_attention_2"
        self.model_name = "parler-tts/parler-tts-mini-v1"
        self.terminate = Event()

        self.model = ParlerTTSForConditionalGeneration.from_pretrained(
            self.model_name,
            attn_implementation=self.attn
        ).to(self.device, self.torch_type)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # self.enable_compile_mode()
        
        self.desc = "Will's voice is monotone yet slightly fast in delivery, with a very close recording that almost has background noise."
        self.sampling_rate = self.model.audio_encoder.config.sampling_rate
        self.frame_rate = self.model.audio_encoder.config.frame_rate

        if self.input_queue is not None:
            #Start a thread to listen on the input queue
            print("Starting thread to listen on input queue")
            self.t = Thread(target=self.listen_queue)
           
   
    def enable_compile_mode(self):
         # compile the forward pass
        compile_mode = "default" # chose "reduce-overhead" for 3 to 4x speed-up
        self.model.generation_config.cache_implementation = "static"
        self.model.forward = torch.compile(self.model.forward, mode=compile_mode)
        # warmup
        inputs = self.tokenizer(
            "This is for compilation",
            return_tensors="pt", 
            padding="max_length", 
            max_length=self.max_len
        ).to(self.device)

        model_kwargs = {**inputs, "prompt_input_ids": inputs.input_ids, "prompt_attention_mask": inputs.attention_mask, }

        n_steps = 1 if compile_mode == "default" else 2
        for _ in range(n_steps):
            _ = self.model.generate(**model_kwargs)

    def stream_generate(self, text, description, play_steps_in_s=1.0):
        play_steps = int(self.frame_rate * play_steps_in_s)
        streamer = ParlerTTSStreamer(self.model, device=self.device, play_steps=play_steps)
        # tokenization
        inputs = self.tokenizer(description, return_tensors="pt").to(self.device)
        prompt = self.tokenizer(text, return_tensors="pt").to(self.device)
        # create generation kwargs
        generation_kwargs = dict(
            input_ids=inputs.input_ids,
            prompt_input_ids=prompt.input_ids,
            attention_mask=inputs.attention_mask,
            prompt_attention_mask=prompt.attention_mask,
            streamer=streamer,
            do_sample=True,
            # temperature=1.0,
            min_new_tokens=20,
        )
        # initialize Thread
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()
        # iterate over chunks of audio
        for new_audio in streamer:
            if new_audio.shape[0] == 0:
                break
            # print(f"Sample of length: {round(new_audio.shape[0] / self.sampling_rate, 4)} seconds")
            yield self.sampling_rate, new_audio


    def generate(self, prompt, description):
        # input_ids = self.tokenizer(description, return_tensors="pt").input_ids.to(self.device)
        # prompt_input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(self.device)
        input = self.tokenizer(description, return_tensors="pt").to(self.device)
        prompt_input = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        ds = datetime.now()
        generation = self.model.generate(
            input_ids=input.input_ids,
            attention_mask=input.attention_mask,
            prompt_input_ids=prompt_input.input_ids,
            prompt_attention_mask=prompt_input.attention_mask,
            do_sample=True,
            )
        de = datetime.now()
        print(f"Time taken: {de-ds}")
        return generation.float().cpu().numpy().squeeze()
    
    def speak(self, prompt, description=None):
        if description is None:
            description = self.desc
        audio_arr = self.generate(prompt, description)
        sd.play(audio_arr)
        sd.wait()

    def stream_speak(self, prompt, description=None):
        if description is None:
            description = self.desc
        for sr, audio_chunk in self.stream_generate(prompt, description):
            sd.play(audio_chunk, samplerate=sr)
            sd.wait()

    def listen_queue(self):
        if self.input_queue is None:
            raise ValueError("Input queue is not set")
        while not self.terminate.is_set():
            try:
                text = self.input_queue.get(timeout=0.1)
                if text:
                    self.stream_speak(text)
                    self.input_queue.task_done()
            except queue.Empty:
                pass
    def stop(self):
        self.terminate.set()
        self.t.join()
# if __name__ == "__main__":
#     tts = ParlerTTS()
#     # tts.speak("Hey, how are you doing today?")
#     tts.stream_speak("Hey, how are you today, what can I do for you?")