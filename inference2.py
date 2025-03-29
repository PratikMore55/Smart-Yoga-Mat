import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model
import tkinter as tk
from PIL import Image, ImageTk

# Load model and labels
model = load_model("model.h5")
label = np.load("labels.npy")

# Initialize Mediapipe Pose
holistic = mp.solutions.pose
holis = holistic.Pose()
drawing = mp.solutions.drawing_utils

# Function to check if person is in frame
def inFrame(lst):
    return (lst[28].visibility > 0.6 and lst[27].visibility > 0.6 
            and lst[15].visibility > 0.6 and lst[16].visibility > 0.6)

# Initialize video capture
cap = cv2.VideoCapture(0)

# Create Tkinter window
root = tk.Tk()
root.title("Yoga Pose Detection")

# Tkinter label to display video
label_widget = tk.Label(root)
label_widget.pack()

def update_frame():
    _, frm = cap.read()
    frm = cv2.flip(frm, 1)
    res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))
    
    if res.pose_landmarks and inFrame(res.pose_landmarks.landmark):
        lst = []
        for i in res.pose_landmarks.landmark:
            lst.append(i.x - res.pose_landmarks.landmark[0].x)
            lst.append(i.y - res.pose_landmarks.landmark[0].y)

        lst = np.array(lst).reshape(1, -1)
        p = model.predict(lst)
        pred = label[np.argmax(p)]
        
        if p[0][np.argmax(p)] > 0.75:
            text = pred
            color = (0, 255, 0)
        else:
            text = "Asana is either wrong or not trained"
            color = (0, 0, 255)

        cv2.putText(frm, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    else:
        cv2.putText(frm, "Make Sure Full Body is Visible", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    drawing.draw_landmarks(frm, res.pose_landmarks, holistic.POSE_CONNECTIONS,
                           connection_drawing_spec=drawing.DrawingSpec(color=(255, 255, 255), thickness=6),
                           landmark_drawing_spec=drawing.DrawingSpec(color=(0, 0, 255), circle_radius=3, thickness=3))
    
    img = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img)
    label_widget.imgtk = imgtk
    label_widget.configure(image=imgtk)
    root.after(10, update_frame)

update_frame()
root.mainloop()

cap.release()
cv2.destroyAllWindows()