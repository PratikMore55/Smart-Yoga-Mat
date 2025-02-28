# AI-Enabled Posture Correction and Health Monitoring for Yoga

## Overview

The AI-Enabled Posture Correction and Health Monitoring for Yoga is an AI-powered yoga monitoring system designed to assist users in maintaining correct yoga postures and tracking vital health metrics. The system integrates sensors, AI models, and a web interface for real-time analysis and feedback.

## Features

---

### • Posture Detection

AI model analyzes yoga poses using a camera.

---

### • Vital Monitoring

Uses a smart wristband with MAX30102 (heart rate & SpO2) and a temperature sensor.

---

### • Guided Yoga Sessions

Audio and visual feedback through an OLED screen and speakers.

---

### • Wireless Communication

ESP32 transmits data to a remote system.

---

### • Web App Integration

Displays real-time metrics and suggestions.

---

## Project Structure

```bash
SmartYogaMat/
│── data_collection.py    # Script for collecting sensor and video data
│── data_training.py      # Training the AI model for yoga posture recognition
│── inference.py         # Running inference to analyze poses and predict corrections
│── main.py             # Main control script for ESP32 and AI integration
│── client.cpp          # Client-side script for real-time data transmission
│── models/             # Pretrained and trained AI models
│── datasets/           # Collected dataset for training
│── web_app/            # Web interface for user interaction
│── requirements.txt    # Required dependencies
│── README.md           # Project documentation
```

---

## Installation

### REQUIREMENTS:

#### HARDWARE:

- ESP32
- MAX30102 Sensor
- Temperature Sensor
- Pressure Sensors
- OLED Screen
- Speakers
- Webcam

#### SOFTWARE:

- Python 3.8+
- OpenCV
- TensorFlow/PyTorch
- Tkinter (for UI)

---

## Setup Instructions

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/smart-yoga-mat.git
   cd smart-yoga-mat
   ```

2. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

3. Run the data collection script:

   ```sh
   python data_collection.py
   ```

4. Train the AI model:

   ```sh
   python data_training.py
   ```

5. Start real-time inference:

   ```sh
   python inference.py
   ```

6. Run the main system:

   ```sh
   python main.py
   ```



