import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import requests

# ESP32 Server IP address and port
esp32_ip = "192.168.87.70"
esp32_port = 70

# Function to fetch images from ESP32-CAM
def get_esp32cam_image():
    try:
        url = f"http://{esp32_ip}/cam-mid.jpg"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            img_array = np.array(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, -1)
            return img
    except Exception as e:
        print(f"Error fetching image from ESP32-CAM: {str(e)}")
    return None

# Path to image directory
path = 'C:/Users/hp/Downloads/AttendRx-Face-Recognition-Attendance-System-main/FaceRecognition_Code_AttendRx/ImagesBasic'
images = []
classNames = []
mylist = os.listdir(path)
print(mylist)

# Load images and class names for face recognition
for cl in mylist:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

# Encode known faces for comparison
def find_encodings(images):
    encodeList = []
    i = 0
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
        print(f'Encoding {i}/{len(mylist)} done!')
        i += 1
    return encodeList

encodelistknown = find_encodings(images)
print('Encoding Complete!')

# Function to mark attendance
def markAttendance(name):
    attendance_url = f"http://{esp32_ip}/display"
    params = {"message": name}
    try:
        response = requests.get(attendance_url, params=params)
        if response.status_code == 200:
            print(f"Attendance marked for {name}")
        else:
            print(f"Failed to mark attendance for {name}")
    except requests.exceptions.RequestException as e:
        print(f"Error marking attendance for {name}: {e}")

# Main loop to capture images and perform face recognition
while True:
    # Capture an image from ESP32-CAM
    img = get_esp32cam_image()

    if img is not None:
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodelistknown, encodeFace)
            faceDis = face_recognition.face_distance(encodelistknown, encodeFace)
            print(faceDis)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                print(name)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                markAttendance(name)

        cv2.imshow('ESP32-CAM', img)
        cv2.waitKey(1)
