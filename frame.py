import cv2
import numpy as np
import mediapipe as mp
import joblib
import pandas as pd
from keras.models import load_model
import time
import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

# Load AI Models
health_model = joblib.load("yoga_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")
pose_model = load_model("model.h5")
pose_labels = np.load("labels.npy")

# MediaPipe Pose Detection Setup
holistic = mp.solutions.pose
holis = holistic.Pose()
drawing = mp.solutions.drawing_utils

# Timer Variables
pose_correct = False
start_time = None
COUNTDOWN = 20
pose_suggestion = ""

# Tkinter GUI Setup
root = tk.Tk()
root.title("Smart Yoga AI Trainer")
root.geometry("800x600")

notebook = ttk.Notebook(root)
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
notebook.add(tab1, text='Health Analysis')
notebook.add(tab2, text='Pose Detection')
notebook.pack(expand=True, fill='both')

# -------------------- Health Input UI --------------------

def analyze_health():
    global pose_suggestion
    age = age_var.get()
    heart_rate = int(hr_var.get())
    spo2 = int(spo2_var.get())
    
    age_category = "15-20" if age < 21 else "21-25"
    input_data = pd.DataFrame([[heart_rate, spo2, age_category]], 
                              columns=['Heart Rate (bpm)', 'SpO2 (%)', 'Age Range'])
    input_data = pd.get_dummies(input_data, columns=['Age Range'])
    
    for col in health_model.feature_names_in_:
        if col not in input_data:
            input_data[col] = 0
    input_data = input_data[health_model.feature_names_in_]
    
    prediction = health_model.predict(input_data)[0]
    health_status = label_encoder.inverse_transform([prediction])[0]
    
    yoga_routines = {
        "Normal": "Tadasana",
        "Healthy": "Trikonasana",
        "Elevated": "Balasana"
    }
    
    pose_suggestion = yoga_routines[health_status]
    result_label.config(text=f"Health Status: {health_status}\nRecommended Pose: {pose_suggestion}")
    display_exercise_image(pose_suggestion)  # Load image immediately

age_label = ttk.Label(tab1, text="Age:", font=("Arial", 16))
age_label.pack()
age_var = tk.IntVar()
age_entry = ttk.Entry(tab1, textvariable=age_var, font=("Arial", 16))
age_entry.pack()

hr_label = ttk.Label(tab1, text="Heart Rate (bpm):", font=("Arial", 16))
hr_label.pack()
hr_var = tk.StringVar()
hr_entry = ttk.Entry(tab1, textvariable=hr_var, font=("Arial", 16))
hr_entry.pack()

spo2_label = ttk.Label(tab1, text="SpO2 (%):", font=("Arial", 16))
spo2_label.pack()
spo2_var = tk.StringVar()
spo2_entry = ttk.Entry(tab1, textvariable=spo2_var, font=("Arial", 16))
spo2_entry.pack()

analyze_button = ttk.Button(tab1, text="Analyze", command=analyze_health)
analyze_button.pack()

result_label = ttk.Label(tab1, text="", font=("Arial", 18, "bold"))
result_label.pack()

# -------------------- Pose Detection UI --------------------
frame1 = ttk.Frame(tab2)
frame2 = ttk.Frame(tab2)
frame1.grid(row=0, column=0, padx=10, pady=10)
frame2.grid(row=0, column=1, padx=10, pady=10)

video_label = tk.Label(frame1)
video_label.pack()

exercise_label = tk.Label(frame2, text="Exercise Image", font=("Arial", 18), bg="white", fg="black")
exercise_label.pack()

timer_label = tk.Label(frame1, text="", font=("Arial", 20, "bold"), fg="black")
timer_label.pack()

cap = cv2.VideoCapture(0)

def display_exercise_image(pose_name):
    folder = "poses/"
    possible_extensions = ["png", "jpg", "jpeg"]
    
    for ext in possible_extensions:
        image_path = f"{folder}{pose_name.lower()}.{ext}"
        if os.path.exists(image_path):
            img = Image.open(image_path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            exercise_img = ImageTk.PhotoImage(img)
            exercise_label.config(image=exercise_img, text="")
            exercise_label.image = exercise_img
            return
    
    exercise_label.config(text=f"Image Not Found: {pose_name}")

def inFrame(lst):
    return all(lst[i].visibility > 0.6 for i in [28, 27, 15, 16])

def update_frame():
    global pose_correct, start_time

    _, frm = cap.read()
    frm = cv2.flip(frm, 1)
    res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))

    if res.pose_landmarks and inFrame(res.pose_landmarks.landmark):
        lst = np.array([[lm.x - res.pose_landmarks.landmark[0].x,
                         lm.y - res.pose_landmarks.landmark[0].y] 
                        for lm in res.pose_landmarks.landmark]).flatten().reshape(1, -1)

        p = pose_model.predict(lst)
        pred = pose_labels[np.argmax(p)]

        if p[0][np.argmax(p)] > 0.75:
            if not pose_correct:
                pose_correct = True
                start_time = time.time()
            elapsed_time = int(time.time() - start_time)
            
            if elapsed_time >= COUNTDOWN:
                text = "Relax"
                color = (0, 255, 0)
                pose_correct = False
                start_time = None
            else:
                text = pred
                color = (0, 255, 0)
                display_exercise_image(pred)
            
            timer_label.config(text=f"Hold: {max(0, COUNTDOWN - elapsed_time)}s")
        else:
            text = "Pose incorrect"
            color = (0, 0, 255)
            pose_correct = False
            start_time = None
            timer_label.config(text="")
    else:
        text = "Ensure full body is visible"
        color = (0, 0, 255)
        pose_correct = False
        start_time = None
        timer_label.config(text="")

    drawing.draw_landmarks(frm, res.pose_landmarks, holistic.POSE_CONNECTIONS)
    frm = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frm)
    img = ImageTk.PhotoImage(img)
    video_label.config(image=img)
    video_label.image = img
    root.after(10, update_frame)

update_frame()
root.mainloop()
cap.release()
cv2.destroyAllWindows()