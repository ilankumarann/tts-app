from abc import ABC, abstractmethod
from queue import Queue
from threading import Thread, Event
import time
from utils.utils import split_acronyms

class BaseTTSEngine(ABC):
    def __init__(self, config=None):
        self.config = config


    @abstractmethod
    def convert_text_to_audio(text:str):
        pass
    
    # def input_pre_processor(self, text):
    #     """
    #     Pre-process the input text before passing it to the model
    #     identifies the date and time and converts it to a readable format
    #     also changes the symbol & to and
    #     """
    #     text = text.replace("&", " and ")
    #     text = split_acronyms(text)
    #     # dates = search_dates(text)
    #     # for d in dates:
    #     #     text = text.replace(d[0], date_time_to_tokens(d[1]))
    #     # Add a blank token to the text
    #     text  = " " + text + " "
    #     return text
