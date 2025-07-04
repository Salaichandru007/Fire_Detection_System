# for image detection
# from deepstack_sdk import ServerConfig, Detection
# import os

# config = ServerConfig("http://localhost:80")
# detection = Detection(config, name="firenetv1")

# response = detection.detectObject(image=os.path.join("images", "fire.jpg"), output=os.path.join("images", "fire_detected.jpg"))

# for obj in response:
#     print("Name: {}, Confidence: {}, x_min: {}, y_min: {}, x_max: {}, y_max: {}".format(obj.label, obj.confidence, obj.x_min, obj.y_min, obj.x_max,
#                    
# 
#                                                                      obj.y_max))
# # for video detection

# from deepstack_sdk import ServerConfig, Detection
# import os

# # Configure the DeepStack server
# config = ServerConfig("http://localhost:80")

# # Initialize the Detection object with your custom model name
# detection = Detection(config, name="firenetv1")

# # Path to the input video
# input_video_path = os.path.join("images", "fire_video.mp4")

# # Path to save the output video with detections
# output_video_path = os.path.join("images", "fire_detected_video.mp4")

# # Run detection on the video
# detections = detection.detectObjectVideo(
#     video=input_video_path,
#     output=output_video_path,
#     min_confidence=0.4,         # Minimum confidence threshold
#     display=True,               # Set True to view live detection (window opens)
#     fps=24,                     # Set FPS if needed
#     output_font_color=(0,0,255) # Red color for detected fire labels
# )

# # Optionally, print all detections frame by frame
# for frame_num, response in detections.items():
#     if response:
#         for obj in response.predictions:
#             print(f"Frame {frame_num}: Label={obj.label}, Confidence={obj.confidence}, Box=({obj.x_min}, {obj.y_min}, {obj.x_max}, {obj.y_max})")


# from camera fire detection

# import cv2
# import requests
# import numpy as np
# import datetime
# import os

# # DeepStack API URL
# API_URL = "http://localhost/v1/vision/custom/firenetv1"

# # Output folder to save fire detected frames
# output_folder = "fire_detected_frames"
# os.makedirs(output_folder, exist_ok=True)

# cap = cv2.VideoCapture("http://localhost:81/stream")  # Change here when ESP32-CAM connected

# if not cap.isOpened():
#     print("Error: Camera could not be opened.")
#     exit()

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Error: Frame not received.")
#         break

#     # Encode frame as JPEG
#     _, img_encoded = cv2.imencode('.jpg', frame)
#     files = {'image': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}

#     # Send frame to DeepStack API
#     try:
#         response = requests.post(API_URL, files=files)
#         data = response.json()
        
#         # Check if fire detected
#         if data["success"] and len(data["predictions"]) > 0:
#             print("🔥 Fire detected!")
#             # Save frame with timestamp
#             timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#             output_path = os.path.join(output_folder, f"fire_{timestamp}.jpg")
#             cv2.imwrite(output_path, frame)
#             cv2.putText(frame, "FIRE DETECTED!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

#     except Exception as e:
#         print("Error communicating with DeepStack:", e)

#     # Display the frame
#     cv2.imshow('Live Fire Detection', frame)

#     # Press 'q' key to quit
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Cleanup
# cap.release()
# cv2.destroyAllWindows()


# version 2 esp32 cam live stream

# import cv2
# import requests
# import numpy as np
# import datetime
# import os

# # DeepStack API URL
# API_URL = "http://localhost/v1/vision/custom/firenetv1"

# # Output folder to save fire detected frames
# output_folder = "fire_detected_frames"
# os.makedirs(output_folder, exist_ok=True)

# # Initialize video capture (0 for webcam, or ESP32-CAM URL)
# # cap = cv2.VideoCapture("http://localhost:81/stream")
# cap = cv2.VideoCapture(0)


# if not cap.isOpened():
#     print("Error: Camera could not be opened.")
#     exit()

# # Colors and font settings
# box_color = (0, 0, 255)  # Red color for fire box
# text_color = (0, 255, 255)  # Yellow for text
# font = cv2.FONT_HERSHEY_SIMPLEX

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Error: Frame not received.")
#         break

#     # Encode frame as JPEG
#     _, img_encoded = cv2.imencode('.jpg', frame)
#     files = {'image': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}

#     # Send frame to DeepStack API
#     try:
#         response = requests.post(API_URL, files=files)
#         data = response.json()

#         # Check if fire detected
#         if data["success"] and len(data["predictions"]) > 0:
#             fire_detected = False
#             for pred in data["predictions"]:
#                 label = pred["label"]
#                 confidence = pred["confidence"]
#                 x_min = int(pred["x_min"])
#                 y_min = int(pred["y_min"])
#                 x_max = int(pred["x_max"])
#                 y_max = int(pred["y_max"])

#                 # Draw bounding box
#                 cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), box_color, 2)

#                 # Write confidence score above box
#                 conf_text = f"{label}: {confidence:.2f}"
#                 cv2.putText(frame, conf_text, (x_min, y_min - 10), font, 0.6, text_color, 2)

#                 fire_detected = True

#             if fire_detected:
#                 # Show "FIRE DETECTED" title on top center
#                 frame_height, frame_width = frame.shape[:2]
#                 cv2.putText(frame, "🔥 FIRE DETECTED 🔥", (frame_width // 4, 40), font, 1, (0, 0, 255), 3)

#                 # Save frame with timestamp
#                 timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#                 output_path = os.path.join(output_folder, f"fire_{timestamp}.jpg")
#                 cv2.imwrite(output_path, frame)

#     except Exception as e:
#         print("Error communicating with DeepStack:", e)

#     # Display the frame
#     cv2.imshow('Live Fire Detection', frame)

#     # Press 'q' key to quit
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Cleanup
# cap.release()
# cv2.destroyAllWindows()


# version 1 for firebase sending ai_confidence

import cv2
import requests
import numpy as np
import datetime
import json
import firebase_admin
from firebase_admin import credentials, db
import os
import time
import config

# --- DeepStack Configuration ---
# IMPORTANT: Replace with the actual IP address where your DeepStack server is running.
#            This is the IP address of the machine (e.g., Raspberry Pi, PC) hosting DeepStack.
#            Based on your DeepStack output, this is 192.168.43.8.

# --- ESP32-CAM Stream URL ---
# IMPORTANT: Replace with the actual IP address of your ESP32-CAM stream.
#            Based on your previous messages, this is 192.168.43.205:81/stream.

# --- Firebase Configuration ---
# 1. Download your Firebase Service Account Key JSON file from:
#    Firebase Console -> Project settings (gear icon) -> Service accounts -> Generate new private key.
# 2. Place this JSON file in the same directory as this Python script.
# 3. Replace 'your-service-account-key.json' with the actual filename of your downloaded key.

# Replace with your Firebase Realtime Database URL (e.g., https://your-project-id-default-rtdb.firebaseio.com/)

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_KEY)
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_DATABASE_URL
    })
    # Firebase path where AI confidence will be sent (e.g., sensor/ai_confidence)
    ref_ai_confidence = db.reference('sensor/ai_confidence')
    print("Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"ERROR: Could not initialize Firebase Admin SDK. Check your service account key path and Firebase URL: {e}")
    exit() # Exit if Firebase initialization fails, as it's critical

# --- AI Detection Parameters ---
# The label your firenet model outputs for fire (e.g., "fire", "flame", "Fire").
# This is used to filter which objects DeepStack detects to consider as 'fire'.
FIRE_LABEL = "fire"  

# --- Stream Processing Parameters ---
# Optional: If your stream is too high resolution for DeepStack, you can resize frames
# Set to None for both to send original frame size. For QVGA (320x240), it's probably fine as is.
RESIZE_WIDTH = None # e.g., 640
RESIZE_HEIGHT = None # e.g., 480

# --- Firebase Update Frequency Control ---
# Variable to keep track of the last confidence sent to Firebase
# Initialize with an impossible value to force the first update.
last_reported_confidence_value = -1.0 
# Only update Firebase if the confidence changes by more than this amount.
# This prevents excessive writes if confidence is stable.
CONFIDENCE_UPDATE_THRESHOLD = 0.02 # e.g., update if confidence changes by 2%

# --- Video Capture Setup ---
cap = cv2.VideoCapture(ESP32_CAM_URL)

if not cap.isOpened():
    print(f"ERROR: Could not open ESP32-CAM stream at {ESP32_CAM_URL}. Check URL and camera power.")
    exit()

print(f"Successfully opened stream from {ESP32_CAM_URL}. Starting AI detection loop...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("WARNING: Could not receive frame from ESP32-CAM. Attempting to reconnect...")
        cap = cv2.VideoCapture(ESP32_CAM_URL) # Try to re-initialize camera capture
        if not cap.isOpened():
            print("ERROR: Failed to reconnect to camera. Exiting.")
            break # Exit the loop if reconnection fails
        time.sleep(1) # Wait a bit before retrying to read frame
        continue # Skip current iteration and try again with the new capture object

    # Resize frame if specified for faster DeepStack processing
    if RESIZE_WIDTH and RESIZE_HEIGHT:
        frame_to_process = cv2.resize(frame, (RESIZE_WIDTH, RESIZE_HEIGHT))
    else:
        frame_to_process = frame

    # Encode frame as JPEG for sending to DeepStack API
    _, img_encoded = cv2.imencode('.jpg', frame_to_process)
    files = {'image': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}

    # Default confidence if no fire detected or an error occurs
    current_ai_confidence = 0.0 

    try:
        # Send frame to DeepStack API with a timeout
        response = requests.post(DEEPSTACK_API_URL, files=files, timeout=10) # 10-second timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data.get("success") and "predictions" in data:
            max_fire_confidence_in_frame = 0.0
            for obj in data["predictions"]:
                # Check if the detected object's label matches our FIRE_LABEL
                if obj.get("label", "").lower() == FIRE_LABEL.lower():
                    # Take the highest confidence value for 'fire' found in this frame
                    max_fire_confidence_in_frame = max(max_fire_confidence_in_frame, obj.get("confidence", 0.0))
            
            current_ai_confidence = max_fire_confidence_in_frame
        
        # Ensure confidence is within a valid 0.0 to 1.0 range
        current_ai_confidence = max(0.0, min(1.0, current_ai_confidence))

    except requests.exceptions.Timeout:
        print(f"WARNING: DeepStack API request timed out for {ESP32_CAM_URL}.")
        current_ai_confidence = -0.01 # Signify timeout error. App Inventor can check for negative values.
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Could not connect to DeepStack API at {DEEPSTACK_API_URL}. Is the server running and IP correct?")
        current_ai_confidence = -0.02 # Signify connection error
    except requests.exceptions.RequestException as req_err:
        print(f"ERROR: DeepStack API request failed: {req_err}")
        current_ai_confidence = -0.03 # Signify general API error
    except json.JSONDecodeError as json_err:
        print(f"ERROR: DeepStack response was not valid JSON: {json_err}")
        current_ai_confidence = -0.04 # Signify invalid JSON response
    except Exception as e:
        print(f"An unexpected error occurred during DeepStack processing: {e}")
        current_ai_confidence = -0.05 # Signify unknown error

    # --- Update Firebase (only if confidence has changed significantly) ---
    # We convert to a float with 2 decimal places for consistent comparison and Firebase storage.
    formatted_current_confidence_for_check = float(f"{current_ai_confidence:.2f}")

    if abs(formatted_current_confidence_for_check - last_reported_confidence_value) > CONFIDENCE_UPDATE_THRESHOLD:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Sending to Firebase: AI_Confidence={formatted_current_confidence_for_check}")
        try:
            # Send the confidence as a string formatted to two decimal places
            ref_ai_confidence.set(f"{formatted_current_confidence_for_check:.2f}")
            last_reported_confidence_value = formatted_current_confidence_for_check
        except Exception as firebase_e:
            print(f"ERROR: Could not send AI confidence to Firebase: {firebase_e}")

    # Optional: Display the frame locally for debugging (requires a display on the server machine)
    # If running on a headless server (e.g., Raspberry Pi without monitor), keep these lines commented out.
    # try:
    #     cv2.imshow('Live Fire Detection (Server Debug)', frame)
    #     if cv2.waitKey(1) & 0xFF == ord('q'): # Press 'q' to quit the script
    #         break
    # except cv2.error as e:
    #     # This error occurs if no display is available (common on headless servers)
    #     pass 

# --- Cleanup ---
cap.release()
# cv2.destroyAllWindows() # Only call if cv2.imshow was used
print("Stream processing and DeepStack detection stopped.")
