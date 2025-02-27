import serial
import threading
import time

stop_thread = False  # Flag to stop thread safely

def read_serial():
    global stop_thread
    ser = serial.Serial('COM3', 115200, timeout=1)  # Change 'COMx' to your port
    while not stop_thread:
        try:
            line = ser.readline().decode().strip()
            if line:
                print(line)  # Process data
        except Exception as e:
            print(f"Error: {e}")
    ser.close()

# Start thread
serial_thread = threading.Thread(target=read_serial, daemon=True)
serial_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    stop_thread = True
    serial_thread.join()
    print("Exiting safely...")
