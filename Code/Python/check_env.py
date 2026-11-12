import mediapipe, pythonosc, serial
print("mediapipe", mediapipe.__version__)
print("pyserial", serial.VERSION)
print("serial.Serial found:", hasattr(serial, "Serial"))
