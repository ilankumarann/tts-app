from datetime import datetime
import torch
import re

def date_time_to_tokens(dt: datetime) -> str:
    """
    Convert a datetime object to a tokenized date string.
    args:
        dt: datetime object
    returns:
        tokens: tokenized date string
    """
    try:
        if dt is None:
            return None
        
        # Convert the date to words (e.g., month names)
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        
        day_names = {
            1: 'first', 2: 'second', 3: 'third', 4: 'fourth',
            5: 'fifth', 6: 'sixth', 7: 'seventh', 8: 'eighth',
            9: 'ninth', 10: 'tenth', 11: 'eleventh', 12: 'twelfth',
            13: 'thirteenth', 14: 'fourteenth', 15: 'fifteenth',
            16: 'sixteenth', 17: 'seventeenth', 18: 'eighteenth',
            19: 'nineteenth', 20: 'twentieth', 30: 'thirtieth',
            31: 'thirty-first'
        }
        
        # Get the month and day names
        month_name = month_names[dt.month]
        day_name = day_names[dt.day]
        
        # Construct the tokenized date string
        tokens = f'{month_name} {day_name} {dt.year}'
        
        return tokens
    
    except ValueError:
        # Handle invalid date strings
        return None
    

def find_device_available():
        if torch.cuda.is_available():
            return "cuda"
        elif torch.mps.is_available():
            return "mps"
        else:
            return "cpu"
        
def split_acronyms(token):
        """
        Split acronyms in the text
        Dont split common words like OR AND etc.
        """
        if token in ["OR", "AND"]:
            return token
        token = re.sub(r"(?<!^)([A-Z])", r" \1", token)
        return token