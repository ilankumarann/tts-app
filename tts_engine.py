from queue import Queue, Empty
from threading import Thread, Event
import logging
logging.basicConfig(level=logging.DEBUG)
from types import GeneratorType

class TTSEngine:
    def __init__(self, backend_name: str):
        self.backend_name = backend_name
        #Defaults
        self.sampling_rate = 16000
        self.stream = False
        self.backend = self.initialize_backend(backend_name)
        
        
    def get_available_backends(self):
        return ["speecht5", "bark", "parler", "kokoro"]
    
    def initialize_backend(self, backend_name: str):
        # Initialize the backend based on the backend_name
        if backend_name == "speecht5":
            from engines.ms_speech_t5 import SpeechT5Backend
            return SpeechT5Backend()
        elif backend_name == "bark":
            raise NotImplementedError("Bark is not yet supported")
        elif backend_name == "kokoro":
            from engines.kokoro_tts import KokoroTTS
            self.stream = True
            self.sampling_rate = 24000
            return KokoroTTS()
        elif backend_name == "parler":
            raise NotImplementedError("Parler TTS is not yet implemented")
        else:
            raise ValueError(f"Unsupported backend: {backend_name}")
        
    def convert_text_to_audio(self, text):
         if self.stream:
             return self.backend.stream_text_to_audio(text)
         
         return self.backend.convert_text_to_audio(text)

   

    # def run(self):
    #     while not self.terminate.is_set():
    #         try:
    #             # Wait for an incoming message from iq
    #             input = self.iq.get(block=True, timeout=0.1)
    #             if input is None:
    #                 continue
                
    #             if isinstance(input, dict):
    #                 session_id = input.get('session_id', None)
    #                 text = input.get("text", None)
                    
    #                 if text == "STOP":
    #                     logging.info("Winding down the process as requested")
    #                     break

    #                 # Use the backend to convert the message to audio
    #                 audio = self.backend.convert_text_to_audio(text)
                    
    #                 # Put the audio into the oq
    #                 self.oq.put({"session_id":session_id, "audio": audio})
    #             else:
    #                 logging.error(f"Format on incoming message is wrong {str(input)}")

    #         except Empty:
    #             continue
    #         except Exception as e:
    #             logging.error(f"Error processing message: {e}")
                #time.sleep(0.1)  # Sleep for a while before retrying

#Example
# if __name__ == "__main__":
    
#     iq = Queue()
#     oq = Queue()
    
#     # Create the TTS engine process
#     tts_engine = TTSEngine(backend_name="speecht5", iq=iq, oq=oq)
#     tts_process = Thread(target=tts_engine.run)
    
#     # Start the TTS engine process
#     tts_process.start()
    
#     # Example of putting a TTS request into the input queue
#     iq.put({"session_id":"12345", "text" :"Hello, this is a test message."})
    
#     # Example of getting a TTS response from the output queue
#     response = oq.get()
#     print(f"Received audio for session {response.get("session_id", None)}")
    
#     # Stop the TTS engine process
#     tts_engine.iq.put({"session_id":"1234", "text": "STOP"})
#     tts_engine.terminate.set()
#     tts_process.join()