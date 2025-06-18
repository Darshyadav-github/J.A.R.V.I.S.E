# command.py
import keyboard
import pyperclip as pi
import threading
import webbrowser
import pyttsx3
import speech_recognition as sr
import eel
import time
import requests
import pyautogui
from playsound import playsound as ps
from bs4 import BeautifulSoup
import os
from typing import Union
from os import getcwd
from engine.keyboard import (
    volumeup, volumedown, open_new_tab, close_tab, open_browser_menu, zoom_in, zoom_out, refresh_page,
    switch_to_next_tab, switch_to_previous_tab, open_history, open_bookmarks, go_back, go_forward,
    open_dev_tools, toggle_full_screen, open_private_window, minimize_window, chrome_task_manager, search_google
)
from engine.SendEmail import send_email  # Ensure this is correctly imported
from engine.GoogleMaps import get_places_info  # Import your function
from engine.file_operations import create_folder_and_files  # Import from file_operations
def is_online(url="https://www.google.com", timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code >= 200 and response.status_code < 300
    except requests.ConnectionError:
        return False
    except requests.Timeout:
        return False
    except Exception as e:
        print(f"Error in is_online function: {e}")
        return False
def generate_audio(message: str, voice: str = "Aditi"):
    url = f"https://api.streamelements.com/kappa/v2/speech?voice={voice}&text={message}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
    try:
        result = requests.get(url=url, headers=headers)
        return result.content
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None
def speak_streamelements(message: str, voice: str = "Aditi", folder: str = "", extension: str = ".mp3") -> Union[None, str]:
    try:
        eel.DisplayMessage(message)
        
        result_content = generate_audio(message, voice)
        if result_content is None:
            raise ValueError("Failed to generate audio from the API.")
        
        file_path = os.path.join(folder, rf"{getcwd()}\{voice}{extension}")
        with open(file_path, "wb") as file:
            file.write(result_content)
        ps(file_path)
        os.remove(file_path)
        
        eel.receiverText(message)
        return None
    except Exception as e:
        print(f"Error in speak_streamelements: {e}")
        return str(e)

def speak_pyttsx3(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 174)
    eel.DisplayMessage(text)
    engine.say(text)
    eel.receiverText(text)
    engine.runAndWait()
def speak(text, voice="Matthew"):
    if is_online():
        speak_streamelements(text, voice)
    else:
        speak_pyttsx3(text)
        
import re

def extract_email(query):
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email = re.search(email_regex, query)
    return email.group(0) if email else None

def provide_directions(location_link):
    webbrowser.open(location_link)
    speak("Here are the directions to your selected location.")
def takecommand():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('listening....')
        eel.DisplayMessage('listening....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        
        audio = r.listen(source, 10, 6)

    try:
        print('recognizing')
        eel.DisplayMessage('recognizing....')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")
        eel.DisplayMessage(query)
        time.sleep(2)
       
    except Exception as e:
        return ""
    
    return query.lower()

@eel.expose
def allCommands(message=1):

    try:
        if message == 1:
            query = takecommand()
            print(query)
            eel.senderText(query)
        else:
            query = message
            eel.senderText(query)

        if "open" in query:
            from engine.features import openCommand
            openCommand(query)
        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)
        elif "create a folder named" in query:
            create_folder_and_files(query)
        elif "create a new file in" in query:
            from engine.file_operations import create_file_in_existing_folder
            create_file_in_existing_folder(query)
        elif "read my selected data" in query:
            speak("Sure sir, reading your selected data")
            keyboard.press_and_release("ctrl + c")
            time.sleep(1)
            clipboard_data = pi.paste()
            speak(clipboard_data)
        elif "image in to text" in query:
            from engine.image_into_text import main
            main()
        elif "message" in query or "phone call" in query or "video call" in query:
            from engine.features import findContact, whatsApp
            contact_no, name = findContact(query)
            flag = ""
            if contact_no != 0:
                if "send message" in query:
                    flag = 'message'
                    speak("What message to send")
                    query, _ = takecommand()
                elif "phone call" in query:
                    flag = 'call'
                else:
                    flag = 'video call'
                whatsApp(contact_no, query, flag, name)
        elif "Todays weather" in query:
            speak("Fetching the weather information.")
            search = "weather today"
            url = f"https://www.google.com/search?q={search}"
            r = requests.get(url)
            data = BeautifulSoup(r.text, "html.parser")
            temp = data.find("div", class_="BNeawe").text
            speak(f"The current weather is {temp}")
        elif "play music" in query:
            speak("What song should I play?")
            song = takecommand()[0]
            webbrowser.open(f"https://open.spotify.com/search/{song}")
            target_tab = 35
            pyautogui.hotkey("tab")
            for i in range(1, target_tab):
                pyautogui.hotkey('tab')
            pyautogui.hotkey('enter')
            speak("Sure sir, here is your music!")
        elif"activate automatic typing" in query:
            from engine.automaticTyping import automaticTyping
            automaticTyping()
        elif "tell a joke" in query:
            speak("Why don't scientists trust atoms? Because they make up everything!")
        elif "what is the time" in query:
            import datetime
            try:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                speak(f"The time is {current_time}")
            except Exception as e:
                error_message = f"An error occurred: {e}"
                print(error_message)
                speak(error_message)
        elif "start eye mouse controller" in query:
            from engine.Eye_mouse_Controller import Eye_mouse_Controller
            Eye_mouse_Controller()
        elif "volume up" in query:
            from engine.keyboard import volumeup
            speak("Turning volume up, sir")
            volumeup()
        elif "volume down" in query:
            from engine.keyboard import volumedown
            speak("Turning volume down, sir")
            volumedown()
        elif "play game" in query:
            from engine.Game import game_play
            game_play()
        elif "enable hand gesture scrolling system" in query:
            from engine.HandGesture import HandGesture
            HandGesture()
        elif "set an alarm for" in query:
            from Time_operation.brain import input_manage_alarm
            input_manage_alarm()
        elif "tell me "in query or "remind me" in query:
            from Time_operation.brain import input_manage_schedule
            input_manage_schedule(query)
        elif "temperature" in query:
            search = query
            url = f"https://www.google.com/search?q={search}"
            r = requests.get(url)
            data = BeautifulSoup(r.text, "html.parser")
            temp = data.find("div", class_="BNeawe").text
            speak(f"Current {search} is {temp}")
        elif "weather" in query:
            search = query
            url = f"https://www.google.com/search?q={search}"
            r = requests.get(url)
            data = BeautifulSoup(r.text, "html.parser")
            temp = data.find("div", class_="BNeawe").text
            speak(f"Current {search} is {temp}")
        elif "send message" in query or "phone call" in query or "video call" in query:
            from engine.features import findContact, whatsApp
            contact_no, name = findContact(query)
            message = ""
            if contact_no != 0:
                if "send message" in query:
                    message = "message"
                    speak("What message to send?")
                    query = takecommand()
                elif "phone call" in query:
                    message = "call"
                else:
                    message = "video call"
                whatsApp(contact_no, query, message, name)
        elif "pause" in query:
            pyautogui.press("k")
            speak("Video paused")
        elif "what is the time" in query or "time please" in query:
            import datetime
            try:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                speak(f"The time is {current_time}")
            except Exception as e:
                error_message = f"An error occurred: {e}"
                print(error_message)
                speak(error_message)
        elif "please tell the internet speed" in query or "what is the internet speed" in query:
            from engine.features import check_internet_speed
            check_internet_speed()
        elif "play" in query:
            pyautogui.press("k")
            speak("Video played")
        elif "mute" in query:
            pyautogui.press("m")
            speak("Video muted")
        # Browser control commands
        elif "open chrome task manager" in query:
            speak("Opening Chrome Task Manager")
            chrome_task_manager()
        elif "minimize current window" in query:
            speak("Minimizing the current window")
            minimize_window()
        elif "open new tab" in query:
            speak("Opening a new tab")
            open_new_tab()
        elif "close tab" in query:
            speak("Closing the tab")
            close_tab()
        elif "open browser menu" in query:
            speak("Opening the browser menu")
            open_browser_menu()
        elif "zoom in" in query:
            speak("Zooming in")
            zoom_in()
        elif "zoom out" in query:
            speak("Zooming out")
            zoom_out()
        elif "refresh page" in query:
            speak("Refreshing the page")
            refresh_page()
        elif "switch to next tab" in query:
            speak("Switching to the next tab")
            switch_to_next_tab()
        elif "switch to previous tab" in query:
            speak("Switching to the previous tab")
            switch_to_previous_tab()
        elif "open history" in query:
            speak("Opening history")
            open_history()
        elif "open bookmarks" in query:
            speak("Opening bookmarks")
            open_bookmarks()
        elif "go back" in query:
            speak("Going back")
            go_back()
        elif "go forward" in query:
            speak("Going forward")
            go_forward()
        elif "open dev tools" in query:
            speak("Opening developer tools")
            open_dev_tools()
        elif "toggle full screen" in query:
            speak("Toggling full screen")
            toggle_full_screen()
        elif "open private window" in query:
            speak("Opening private window")
            open_private_window()
        elif "search google for" in query:
            search_query = query.split("search google for")[-1].strip()
            speak(f"Searching Google for {search_query}")
            search_google(search_query)
        elif "start object detection" in query:
            from app import main
            speak("Starting object detection")
        elif "generate an image" in query:
            from engine.features import generateImageFromPrompt
            generateImageFromPrompt(query)
        else:
            from engine.features import chatBot as chatWithGPT
            chatWithGPT(query)
    except Exception as e:
        print(f"Error in allCommands: {e}")

    eel.ShowHood()