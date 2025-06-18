import cv2
import mediapipe as mp
import pyautogui

# Initialize the webcam
cam = cv2.VideoCapture(0)

# Initialize the Face Mesh detector with refined landmarks
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# Get screen width and height
screen_w, screen_h = pyautogui.size()

def calculate_eye_aspect_ratio(eye_landmarks):
    # Get the vertical landmarks
    vertical_1 = eye_landmarks[1]
    vertical_2 = eye_landmarks[5]
    
    # Get the horizontal landmarks
    horizontal_1 = eye_landmarks[0]
    horizontal_2 = eye_landmarks[3]
    
    # Calculate the distances
    vertical_distance = ((vertical_1.x - vertical_2.x) ** 2 + (vertical_1.y - vertical_2.y) ** 2) ** 0.5
    horizontal_distance = ((horizontal_1.x - horizontal_2.x) ** 2 + (horizontal_1.y - horizontal_2.y) ** 2) ** 0.5
    
    # Calculate the eye aspect ratio
    ear = vertical_distance / horizontal_distance
    return ear

while True:
    # Read a frame from the webcam
    ret, frame = cam.read()
    if not ret:
        break

    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the RGB frame to detect face mesh
    output = face_mesh.process(rgb_frame)
    landmarks_points = output.multi_face_landmarks

    # Get frame height and width
    frame_h, frame_w, _ = frame.shape

    if landmarks_points:
        landmarks = landmarks_points[0].landmark

        # Move mouse pointer based on specific landmarks
        for id, landmark in enumerate(landmarks[474:478]):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
            if id == 1:
                screen_x = screen_w / frame_w * x
                screen_y = screen_h / frame_h * y
                pyautogui.moveTo(screen_x, screen_y)
                print(f"Mouse moved to: {screen_x}, {screen_y}")  # Debugging line

        # Detect eye blink to trigger mouse click
        left_eye_landmarks = [landmarks[i] for i in [33, 160, 158, 133, 153, 144]]
        
        # Calculate the eye aspect ratio for the left eye
        left_ear = calculate_eye_aspect_ratio(left_eye_landmarks)

        print(f"Left eye aspect ratio: {left_ear}")  # Debugging line

        # Check for eye blink with a threshold for testing
        if left_ear < 0.2:  # Adjust the threshold based on testing
            print("Eye blink detected, clicking mouse...")  # Debugging line
            pyautogui.click()
            pyautogui.sleep(1)
        else:
            print("No blink detected")  # Debugging line

    else:
        print("No landmarks detected")  # Debugging line

    # Display the frame
    cv2.imshow("Eye Controlled Mouse", frame)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cam.release()
cv2.destroyAllWindows()
calculate_eye_aspect_ratio()