import requests
import json
import base64
import cv2

# Function to capture an image from the computer's camera and save it
def capture_image_and_save(image_path="captured_image.png"):
    # Initialize the camera
    cap = cv2.VideoCapture(0)  # 0 is the default camera

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return False

    try:
        # Capture a single frame
        ret, frame = cap.read()

        if ret:
            # Save the image in PNG format
            cv2.imwrite(image_path, frame)
            print(f"Image captured and saved as {image_path}")
            return True
        else:
            print("Error: Could not capture image.")
            return False
    finally:
        # Release the camera
        cap.release()
        cv2.destroyAllWindows()

# Function to encode an image to Base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

# Function to send the encoded image to the API and get a response
def brain(encoded_image):
    url = "https://api.deepinfra.com/v1/openai/chat/completions"

    headers = {
        "accept": "text/event-stream",
        "Content-Type": "application/json",  # Added content-type header
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        "x-deepinfra-source": "model-embed"
    }

    payload = {
        "model": "llava-hf/llava-1.5-7b-hf",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "What is written in this image?"
                    }
                ]
            }
        ]
    }

    # Convert the payload to JSON
    payload_json = json.dumps(payload)

    # Make the POST request
    response = requests.post(url, headers=headers, data=payload_json)

    # Check if the request was successful
    if response.status_code == 200:
        response_str = response.content.decode('utf-8')
        data = json.loads(response_str)
        answer = data['choices'][0]['message']['content']
        return answer
    else:
        print(f"Error: API request failed with status code {response.status_code}")
        return None

def main():
    while True:
        x = input("Enter your command: ")
        if "what is this" in x:
            image_path = "captured_image.png"
            if capture_image_and_save(image_path):
                encoded_image = encode_image_to_base64(image_path)
                answer = brain(encoded_image)
                if answer:
                    print(answer, end="", flush=True)
