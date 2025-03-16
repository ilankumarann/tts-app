import nltk
from nltk.tokenize import word_tokenize
from datetime import datetime

# Define a function to convert ISO date format to tokens
def iso_to_tokens(date_str):
    try:
        # Parse the date string into a datetime object
        dt = datetime.strptime(date_str, '%Y%m%d')
        
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
        tokens = f'{month_name} {day_name}{dt.year}'
        
        return tokens
    
    except ValueError:
        # Handle invalid date strings
        return None

# Generate training data
train_data = []
date_formats = ['%Y%m%d', '%d-%m-%Y', '%m/%d/%Y']
for date_format in date_formats:
    dates = [f'{i:04d}{j:02d}' for i in range(1, 32) for j in range(1, 31)]
    for date_str in dates:
        tokens = iso_to_tokens(date_str)
        if tokens is not None:
            train_data.append((date_str, tokens))

# Save the training data to a CSV file
import csv
with open('train_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['input_date', 'output_token'])
    for date_str, tokens in train_data:
        writer.writerow([date_str, tokens])