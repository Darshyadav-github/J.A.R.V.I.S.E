import re
from os import getcwd

# Function to parse schedule input
def parse_schedule_input(input_text):
    # Regular expression to extract time in format like "07:30 PM" or "8:00pm"
    time_regex = r'(\d{1,2}:\d{2} ?(?:AM|PM|am|pm))'
    
    # Find all matches of time in the input text
    times = re.findall(time_regex, input_text)
    
    if times:
        # Assuming the first time found is the intended time
        time_match = times[0]

        # Normalize the time format to "hh:mmAM/PM"
        formatted_time = time_match.strip().replace(" ", "").upper()
        updated_input_text = input_text.replace(time_match, "").replace("at", "").replace("tell me", "").replace("Tell me", "").replace("to", "").strip()
        
        # Combine formatted time with command
        formatted_output = f"{formatted_time} = Sir, this is your {updated_input_text} time"
        
        return formatted_output, formatted_time
    else:
        return "No valid time found in input", None

# Function to save schedule to a file
def save_schedule_to_file(output_text, time, filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        lines = []

    time_found = False
    with open(filename, 'w') as file:
        for line in lines:
            if line.startswith(time):
                file.write(output_text + '\n')
                time_found = True
            else:
                file.write(line)
        if not time_found:
            file.write(output_text + '\n')  # Ensure new entries are written on a new line

def save_schedule_to_file_append(output_text, filename):
    with open(filename, 'a') as file:
        file.write(output_text + '\n')  # Appending text with a newline

# Function to manage schedule input
def input_manage_schedule(input_text):
    output, time = parse_schedule_input(input_text)

    if output != "No valid time found in input":
        save_schedule_to_file_append(output, fr'{getcwd()}\schedule.txt')
    else:
        print(output)

# Function to parse alarm input
def parse_alarm_input(input_text):
    # Regular expression to extract time in format like "07:30 PM" or "8:00pm"
    time_regex = r'(\d{1,2}:\d{2} ?(?:AM|PM|am|pm))'
    
    # Find all matches of time in the input text
    times = re.findall(time_regex, input_text)
    
    if times:
        # Assuming the first time found is the intended time
        time_match = times[0]

        # Normalize the time format to "hh:mmAM/PM"
        formatted_time = time_match.strip().replace(" ", "").upper()

        return formatted_time
    else:
        return "No valid time found in input"

# Function to save alarm to a file
def save_alarm_to_file_append(time, filename):
    with open(filename, 'a') as file:
        file.write(f"Alarm set for {time}\n")  # Appending alarm time with a newline

# Function to manage alarm input
def input_manage_alarm(input_text):
    time = parse_alarm_input(input_text)

    if time != "No valid time found in input":
        save_alarm_to_file_append(time, r'C:\Users\marke\Documents\jarvis-main\Alarm_data.txt')
    else:
        print(time)

# Example usage:
