import multiprocessing
import sys
import os
import time
import speech_recognition as sr
from playsound import playsound
import pyautogui as autogui

# Local modules
from Time_operation.throw_alert import check_schedule, check_alarm

# File paths
file_path = r'C:\Users\marke\Documents\jarvis-main\schedule.txt'
alarm_file_path = r'C:\Users\marke\Documents\jarvis-main\Alarm_data.txt'

# --- Hotword Listener ---
def hotword_listener():
    HOTWORD = "jarvis"

    def play_activation_sound():
        sound_path = r"ASSETS\SOUNDS\activation_sound.wav"
        if os.path.exists(sound_path):
            playsound(sound_path)

    recognizer = sr.Recognizer()

    try:
        mic = sr.Microphone()
    except OSError:
        print("❌ No microphone found.")
        return

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    print("🎧 Hotword listener active...")

    while True:
        try:
            with mic as source:
                print("🎧 Listening...")
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)

            transcript = recognizer.recognize_google(audio).lower()

            if HOTWORD in transcript.split():
                print("✅ Hotword detected!")
                play_activation_sound()
                print("🔵 Sending Win + J...")

                # Send Win + J
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")

                # Pause listener while accepting user command
                print("🎤 Speak your command...")
                with mic as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    command_audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)

                try:
                    command = recognizer.recognize_google(command_audio).lower()
                    print(f"🎙️ You said: {command}")
                    # You can pass this command to Jarvis or trigger logic here
                except sr.UnknownValueError:
                    print("❌ Could not understand your command.")
                except sr.RequestError as err:
                    print(f"⚠️ Google API error while recognizing command: {err}")

        except sr.UnknownValueError:
            continue
        except sr.RequestError as err:
            print(f"⚠️ API request error: {err}", file=sys.stderr)
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)

# --- Jarvis Core ---
def startJarvis():
    print("🧠 Starting Jarvis...")
    from main import main
    main()

# --- Start Processes ---
if __name__ == '__main__':
    multiprocessing.freeze_support()

    p1 = multiprocessing.Process(target=startJarvis)
    p2 = multiprocessing.Process(target=hotword_listener)
    p3 = multiprocessing.Process(target=check_schedule, args=(file_path,))
    p4 = multiprocessing.Process(target=check_alarm, args=(alarm_file_path,))

    p1.start()
    p2.start()
    p3.start()
    p4.start()

    p1.join()
    p3.join()
    p4.join()

    if p2.is_alive():
        p2.terminate()
        p2.join()
    else:
        print("🔒 Access Denied.")
