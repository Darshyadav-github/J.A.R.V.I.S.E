import threading
import cv2
import FaceRecognition as fr
import os
import eel
from engine.features import *
from engine.command import *
import datetime
import pyttsx3

# Initialize face recognizer
try:
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.read('trainingData.yml')
except AttributeError:
    print("Error: 'cv2.face' module or 'LBPHFaceRecognizer_create' function is not available. Ensure you have 'opencv-contrib-python' installed.")
    exit(1)

name = {0: "Darsh"}
cap = cv2.VideoCapture(0)

face_authenticated = False
clap_detected = False

def check_face(frame):
    global face_authenticated
    faces_detected, gray_img = fr.faceDetection(frame)
    for face in faces_detected:
        (x, y, w, h) = face
        roi_gray = gray_img[y:y+w, x:x+h]
        label, confidence = face_recognizer.predict(roi_gray)
        print(f"Label: {label}, Confidence: {confidence}")
        fr.draw_rect(frame, face)
        predicted_name = name.get(label, "Unknown")
        if confidence < 60:
            fr.put_text(frame, predicted_name, x, y)
            if predicted_name == "Darsh":
                face_authenticated = True
                break

def recognize_faces():
    global face_authenticated
    while not face_authenticated:
        ret, frame = cap.read()
        if ret:
            check_face(frame)
            resized_img = cv2.resize(frame, (1000, 700))
            cv2.imshow('Face Recognition', resized_img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def start_jarvis():
    eel.init("www")
    os.system('start msedge.exe --app="http://localhost:8000/index.html"')
    eel.start('index.html', mode=None, host='localhost', block=True)

def greet_user():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning!")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am Jarvis. How may I help you, sir?")

def main():
    print("Starting face recognition...")
    recognize_thread = threading.Thread(target=recognize_faces)
    recognize_thread.start()
    recognize_thread.join()

    if face_authenticated:
        print("Face recognized. Starting Jarvis...")
        greet_user()
        start_jarvis()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    face_recognition_thread = threading.Thread(target=main)
    face_recognition_thread.start()
    face_recognition_thread.join()
