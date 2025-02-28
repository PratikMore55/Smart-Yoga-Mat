import socket
import tkinter as tk
from tkinter import ttk
import joblib
import pandas as pd
import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model
from PIL import Image, ImageTk
from threading import Thread

# Load AI Models
health_model = joblib.load("yoga_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")
pose_model = load_model("model.h5")
pose_labels = np.load("labels.npy")

# MediaPipe Pose
holistic = mp.solutions.pose
holis = holistic.Pose()
drawing = mp.solutions.drawing_utils

# OpenCV Video Capture
cap = cv2.VideoCapture(0)

# Yoga Routine Recommendations
yoga_routines = {
    "Normal": ["Tadasana", "Vrikshasana", "Bhujangasana"],
    "Healthy": ["Tadasana", "Surya Namaskar", "Dhanurasana"],
    "Elevated": ["Tadasana", "Anulom Vilom", "Shavasana"]
}

# Server Details
HOST = '0.0.0.0'
PORT = 5000

# Tkinter GUI Setup
root = tk.Tk()
root.title("AI-Powered Yoga Analyzer")

# UI Elements
pose_name = tk.StringVar(value="")
pose_label = ttk.Label(root, textvariable=pose_name, font=("Arial", 16))
pose_label.pack()
pose_image_label = tk.Label(root)
pose_image_label.pack()
camera_label = tk.Label(root)
camera_label.pack()

timer_label = ttk.Label(root, text="", font=("Arial", 16))
timer_label.pack()

result_label = ttk.Label(root, text="Waiting for Data...")
result_label.pack()

classified_pose_label = ttk.Label(root, text="Pose Detected: None", font=("Arial", 14))
classified_pose_label.pack()

# Data Storage
data_list = []
MAX_DATA = 10
FINAL_AVG_COUNT = 5

pose_sequence = []
current_exercise_index = 0
current_set = 1

# Load Pose Image
def load_pose_image(pose):
    try:
        img_path = f"poses/{pose}.jpg"
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (300, 300))
        imgtk = ImageTk.PhotoImage(Image.fromarray(img))
        pose_image_label.config(image=imgtk)
        pose_image_label.image = imgtk
    except:
        pose_image_label.config(text="Image Not Found")

# Health Analysis
def analyze_health(avg_hr, avg_spo2):
    input_data = pd.DataFrame([[avg_hr, avg_spo2, "21-25"]],
                              columns=['Heart Rate (bpm)', 'SpO2 (%)', 'Age Range'])
    input_data = pd.get_dummies(input_data, columns=['Age Range'])
    for col in health_model.feature_names_in_:
        if col not in input_data:
            input_data[col] = 0
    input_data = input_data[health_model.feature_names_in_]
    prediction = health_model.predict(input_data)[0]
    health_status = label_encoder.inverse_transform([prediction])[0]

    yoga_poses = yoga_routines.get(health_status, [])
    result_label.config(text=f"Health Status: {health_status}\nRecommended Yoga: {', '.join(yoga_poses)}")

    global pose_sequence, current_exercise_index, current_set
    pose_sequence = yoga_poses
    current_exercise_index = 0
    current_set = 1
    start_workout()

# Workout Routine
def start_workout():
    global current_exercise_index, current_set
    if current_exercise_index < len(pose_sequence):
        pose = pose_sequence[current_exercise_index]
        pose_name.set(f"{pose} - Set {current_set}/3")
        load_pose_image(pose)
        countdown(30, pose, perform_exercise)
    else:
        timer_label.config(text="Workout Complete!")

# Countdown Function
def countdown(seconds, pose, next_step):
    if seconds >= 0:
        timer_label.config(text=f"{pose}: {seconds}s")
        root.after(1000, lambda: countdown(seconds - 1, pose, next_step))
    else:
        next_step()

# Perform Exercise
def perform_exercise():
    global current_set, current_exercise_index
    if current_set < 3:
        current_set += 1
        timer_label.config(text="Rest for 20s")
        root.after(20000, start_workout)
    else:
        current_set = 1
        current_exercise_index += 1
        start_workout()

# Improved Pose Detection
def inFrame(landmarks):
    return landmarks[28].visibility > 0.6 and landmarks[27].visibility > 0.6 and \
           landmarks[15].visibility > 0.6 and landmarks[16].visibility > 0.6

# Live Camera Feed with Improved Pose Classification
def update_camera():
    ret, frm = cap.read()
    if ret:
        frm = cv2.flip(frm, 1)
        res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))

        if res.pose_landmarks and inFrame(res.pose_landmarks.landmark):
            drawing.draw_landmarks(frm, res.pose_landmarks, holistic.POSE_CONNECTIONS)
            
            landmarks = []
            for lm in res.pose_landmarks.landmark:
                landmarks.extend([lm.x - res.pose_landmarks.landmark[0].x,
                                  lm.y - res.pose_landmarks.landmark[0].y])  # Normalize to first landmark
            
            landmarks = np.array(landmarks).reshape(1, -1)
            prediction = pose_model.predict(landmarks)
            pose_index = np.argmax(prediction)
            detected_pose = pose_labels[pose_index]

            if prediction[0][pose_index] > 0.75:
                classified_pose_label.config(text=f"Pose Detected: {detected_pose}")
            else:
                classified_pose_label.config(text="Asana is either wrong or not trained")

        img = Image.fromarray(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))
        img = img.resize((300, 300))
        imgtk = ImageTk.PhotoImage(image=img)
        camera_label.imgtk = imgtk
        camera_label.configure(image=imgtk)

    camera_label.after(10, update_camera)

update_camera()

# Server Function
def start_server():
    global data_list
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print("Server listening on port", PORT)

    conn, addr = server_socket.accept()
    print(f"Connected by {addr}")

    try:
        while len(data_list) < MAX_DATA:
            data = conn.recv(1024).decode().strip()
            if not data:
                continue
            print("Received:", data)
            try:
                heart_rate, spo2 = map(float, data.split(","))
                data_list.append((heart_rate, spo2))
            except ValueError:
                print("Invalid data format, skipping...")
                continue

        last_values = data_list[-FINAL_AVG_COUNT:]
        avg_hr = sum(hr for hr, _ in last_values) / FINAL_AVG_COUNT
        avg_spo2 = sum(spo2 for _, spo2 in last_values) / FINAL_AVG_COUNT

        analyze_health(avg_hr, avg_spo2)

    finally:
        conn.close()
        server_socket.close()

thread = Thread(target=start_server, daemon=True)
thread.start()

root.mainloop()
cap.release()
cv2.destroyAllWindows()
