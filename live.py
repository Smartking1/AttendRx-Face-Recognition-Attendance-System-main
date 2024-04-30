import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import requests

# ESP32-CAM IP address
esp32cam_url = 'http://192.168.80.70/cam-mid.jpg'

# Function to fetch images from ESP32-CAM
def get_esp32cam_image():
    try:
        response = requests.get(esp32cam_url, timeout=10)
        if response.status_code == 200:
            img_array = np.array(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, -1)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return img, img_gray
    except Exception as e:
        print(f"Error fetching image from ESP32-CAM: {str(e)}")
    return None, None

# Load known images and encodings
path = 'C:/Users/hp/Downloads/AttendRx-Face-Recognition-Attendance-System-main/FaceRecognition_Code_AttendRx/ImagesBasic'
images = [cv2.imread(os.path.join(path, cl)) for cl in os.listdir(path)]
classNames = [os.path.splitext(cl)[0] for cl in os.listdir(path)]
encodelistknown = [face_recognition.face_encodings(img)[0] for img in images]

print('Encoding Complete!')

# Variables for liveliness detection and face filtering
prev_gray = None
face_size_threshold = 10000  # Adjust this based on face size in your setup
min_face_width_ratio = 0.2
max_face_width_ratio = 0.8
min_face_height_ratio = 0.2
max_face_height_ratio = 0.8

while True:
    # Capture an image from ESP32-CAM
    img_color, img_gray = get_esp32cam_image()

    if img_color is not None and img_gray is not None:
        imgS = cv2.resize(img_color, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        # Liveliness detection: Compare consecutive frames
        if prev_gray is not None:
            frame_diff = cv2.absdiff(prev_gray, img_gray)
            motion_score = np.mean(frame_diff)

            # Adjust this threshold based on your setup
            if motion_score > 10:  # Example threshold for motion detection
                print("Motion detected - Liveliness confirmed!")
            else:
                print("Possible static image or no motion detected!")

        # Update previous frame for next iteration
        prev_gray = img_gray.copy()

        for (top, right, bottom, left), encodeFace in zip(faceCurFrame, encodesCurFrame):
            # Calculate face size
            face_width = right - left
            face_height = bottom - top
            face_area = face_width * face_height

            # Check if the detected face is within reasonable size and position
            if (face_area > face_size_threshold and
                min_face_width_ratio * imgS.shape[1] < face_width < max_face_width_ratio * imgS.shape[1] and
                min_face_height_ratio * imgS.shape[0] < face_height < max_face_height_ratio * imgS.shape[0]):

                matches = face_recognition.compare_faces(encodelistknown, encodeFace)
                faceDis = face_recognition.face_distance(encodelistknown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    print(name)
                    cv2.rectangle(img_color, (left * 4, top * 4), (right * 4, bottom * 4), (0, 255, 0), 2)
                    cv2.rectangle(img_color, (left * 4, bottom * 4 - 35), (right * 4, bottom * 4), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img_color, name, (left * 4 + 6, bottom * 4 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    markAttendance(name)
                else:
                    # Face unrecognized: Draw red bounding box and display message
                    cv2.rectangle(img_color, (left * 4, top * 4), (right * 4, bottom * 4), (0, 0, 255), 2)
                    cv2.putText(img_color, "Face Unrecognized", (left * 4 + 6, bottom * 4 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow('ESP32-CAM', img_color)
        cv2.waitKey(1)
