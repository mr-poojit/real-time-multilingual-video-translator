import cv2
import pyaudio
import wave
import threading

video_capture = cv2.VideoCapture(0) 

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  

audio = pyaudio.PyAudio()

print("Video Capture Opened:", video_capture.isOpened())
print("PyAudio Version:", audio.get_default_host_api_info())
