import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Function to calculate Euclidean distance between two points
def get_distance(a, b):
    return np.hypot(b[0] - a[0], b[1] - a[1])

# Screen dimensions
screen_width, screen_height = pyautogui.size()

# MediaPipe Hands initialization
mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)

draw = mp.solutions.drawing_utils

# Function to find index finger tip, middle finger tip, and thumb tip
def find_finger_tips(processed):
    if processed.multi_hand_landmarks:
        hand_landmarks = processed.multi_hand_landmarks[0]  # Assuming only one hand is detected
        index_finger_tip = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
        middle_finger_tip = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_TIP]
        thumb_tip = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_TIP]
        return index_finger_tip, middle_finger_tip, thumb_tip
    return None, None, None

# Function to detect scroll gesture
def is_scroll(landmark_list):
    index_middle_dist = get_distance(landmark_list[8], landmark_list[12])
    return index_middle_dist < 0.05, index_middle_dist  # Adjust threshold based on your need

# Function to detect click gesture
def is_click(landmark_list):
    thumb_index_dist = get_distance(landmark_list[4], landmark_list[8])
    return thumb_index_dist < 0.04  # Adjust threshold based on your need

# Function to map hand coordinates to screen coordinates
def map_coordinates(x, y, frame_width, frame_height):
    return int(x * screen_width), int(y * screen_height)

# Function to detect gesture and perform corresponding action
def detect_gesture(frame, landmark_list, processed):
    if len(landmark_list) >= 21:
        index_finger_tip, middle_finger_tip, thumb_tip = find_finger_tips(processed)
        if index_finger_tip and middle_finger_tip and thumb_tip:
            # Move cursor with index finger
            cursor_x, cursor_y = map_coordinates(index_finger_tip.x, index_finger_tip.y, frame.shape[1], frame.shape[0])
            pyautogui.moveTo(cursor_x, cursor_y)

            scroll_detected, index_middle_dist = is_scroll(landmark_list)
            if scroll_detected:
                # Determine scroll direction based on finger positions
                if index_finger_tip.y < middle_finger_tip.y:  # Scroll up
                    pyautogui.scroll(20)  # Adjust the scrolling increment as needed
                    cv2.putText(frame, "Scrolling Up", (180, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif index_finger_tip.y > middle_finger_tip.y:  # Scroll down
                    pyautogui.scroll(-20)  # Adjust the scrolling increment as needed
                    cv2.putText(frame, "Scrolling Down", (180, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:  # Pause scrolling
                    cv2.putText(frame, "Scrolling Paused", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                # Detect click gesture
                click_detected = is_click(landmark_list)
                if click_detected:
                    pyautogui.click()
                    cv2.putText(frame, "Click", (180, 220), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

# Function to initialize camera and perform hand gesture recognition
def MCV():
    cap = cv2.VideoCapture(0)

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            processed = hands.process(frameRGB)

            landmark_list = []
            if processed.multi_hand_landmarks:
                hand_landmarks = processed.multi_hand_landmarks[0]  # Assuming only one hand is detected
                draw.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS)
                for lm in hand_landmarks.landmark:
                    landmark_list.append((lm.x, lm.y))

            detect_gesture(frame, landmark_list, processed)

            cv2.imshow('Hand Gesture Control', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

# Run the main function
MCV()
