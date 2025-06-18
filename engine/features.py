# features.py
import hugchat
import os
import requests
import openai
from PIL import Image
import sqlite3
import struct
import subprocess
import time
import webbrowser
import pyaudio
import pyautogui
import pvporcupine
from engine.config import ASSISTANT_NAME
from engine.helper import extract_yt_term, remove_words
from engine.command import speak, takecommand
from email.message import EmailMessage
import smtplib
from playsound import playsound
import pywhatkit as kit 
from hugchat import hugchat
from pipes import quote
from time import sleep
import eel
con = sqlite3.connect("jarvis.db")
cursor = con.cursor()
dictapp = {"commandprompt":"cmd","paint":"paint","word":"winword","excel":"excel","chrome":"chrome","vscode":"code","powerpoint":"powerpnt"}

@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")

       

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()



# find contacts
def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
def whatsApp(mobile_no, message, flag, name):
    

    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)

# chat bot 
def chatWithGPT(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        response_text = ""
        for chunk in response:
            chunk_message = chunk['choices'][0].get('delta', {}).get('content', '')
            response_text += chunk_message
        
        speak(response_text)
        return response_text
    except Exception as e:
        print(f"Error: {e}")
        speak("Sorry, I couldn't connect to the AI service.")
        return "I'm having trouble accessing the AI service right now."
def generateImageFromPrompt(prompt):
    """Generate an image from a prompt using OpenAI's API."""
    try:
        speak("Generating image, please wait...")
        # Using the available DALL-E model (e.g., dall-e-3)
        response = openai.Image.create(
            model="dall-e-3",  # You can switch this to dall-e-2 if needed
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="url"  # Ensures the response is a URL
        )
        image_url = response['data'][0]['url']
        res = requests.get(image_url)
        
        # Save the image locally
        with open("generated_image.png", "wb") as image:
            image.write(res.content)
        
        # Open and display the image
        img = Image.open("generated_image.png")
        img.show()
        
        speak("Here is the image you requested.")
    except Exception as e:
        print(f"Error: {e}")
        speak("Sorry, I couldn't generate the image.")
# android automation



def closeappweb(query):
    speak("Closing, sir")
    if "one tab" in query or "1 tab" in query:
        pyautogui.hotkey("ctrl", "w")
        speak("Tab closed")
    elif "2 tab" in query:
        pyautogui.hotkey("ctrl", "w")
        sleep(0.5)
        pyautogui.hotkey("ctrl", "w")
        speak("Tabs closed")
    elif "3 tab" in query:
        pyautogui.hotkey("ctrl", "w")
        sleep(0.5)
        pyautogui.hotkey("ctrl", "w")
        sleep(0.5)
        pyautogui.hotkey("ctrl", "w")
        speak("Tabs closed")
    elif "4 tab" in query:
        pyautogui.hotkey("ctrl", "w")
        sleep(0.5)
        pyautogui.hotkey("ctrl", "w")
        sleep(0.5)
        pyautogui.hotkey("ctrl", "w")
        sleep(0.5)
        pyautogui.hotkey("ctrl", "w")
        speak("Tabs closed")
    elif "5 tab" in query:
        pyautogui.hotkey("ctrl", "w")
        sleep(0.5)
        pyautogui.hotkey("ctrl", "w")
        sleep(0.5)
        pyautogui.hotkey("ctrl", "w")
        sleep(0.5)
        pyautogui.hotkey("ctrl", "w")
        sleep(0.5)
        pyautogui.hotkey("ctrl", "w")
        speak("Tabs closed")
    else:
        dictapp = {"commandprompt":"cmd", "paint":"paint", "word":"winword", "excel":"excel", "chrome":"chrome", "vscode":"code", "powerpoint":"powerpnt"}
        keys = list(dictapp.keys())
        for app in keys:
            if app in query:
                os.system(f"taskkill /f /im {dictapp[app]}.exe")
                speak(f"Closed {app}")

def chatBot(query):
    user_input = query.lower()

    # Inject context prompt to return short replies unless user asks for full info
    short_prompt = (
        f"{user_input}\n\n"
        "Reply only with basic and brief information unless the user asks for more detail, "
        "like 'give full info', 'explain in detail', or 'tell me everything'."
    )

    try:
        chatbot = hugchat.ChatBot(cookie_path="engine\\cookies.json")
        id = chatbot.new_conversation()
        chatbot.change_conversation(id)

        response = chatbot.chat(short_prompt)
        response_text = str(response).strip()

        speak(response_text)
        return response_text

    except Exception as e:
        print(f"Error in chatbot: {e}")
        speak("Sorry, I'm having trouble responding right now.")
        return "An error occurred while processing your request."
