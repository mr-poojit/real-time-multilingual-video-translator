import cv2
import pyaudio
import wave
import threading
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile
import os
import pygame
import traceback

# Audio capture parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Sample rate recommended for speech recognition

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Get audio input device index (optional)
# DEVICE_INDEX = None  # You can specify the device index if needed

# Initialize Speech Recognition and Pygame
recognizer = sr.Recognizer()
pygame.mixer.init()

# Global variable to hold the translated text for subtitles
translated_text = ''

# Function to check and initialize the camera
def initialize_camera():
    cap = None
    # List of camera indices to try
    indices = [0, 1, 2, 3, -1]
    # List of backends to try based on the operating system
    backends = []

    # Determine backend based on the platform
    os_name = cv2.getBuildInformation()
    if 'Windows' in os_name:
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_VFW]
    elif 'Darwin' in os_name:  # macOS
        backends = [cv2.CAP_AVFOUNDATION, cv2.CAP_QT]
    elif 'Linux' in os_name:
        backends = [cv2.CAP_V4L2, cv2.CAP_GSTREAMER]
    else:
        backends = [cv2.CAP_ANY]

    for backend in backends:
        for index in indices:
            print(f"Trying camera index {index} with backend {backend}")
            cap = cv2.VideoCapture(index, backend)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"Camera opened successfully with index {index} and backend {backend}")
                    return cap
                else:
                    print("Failed to read a frame from the camera")
                cap.release()
            else:
                print(f"Failed to open camera with index {index} and backend {backend}")
    print("No working camera found. Exiting program.")
    exit()

# Initialize the camera
video_capture = initialize_camera()

def recognize_and_translate_audio(audio_data):
    global translated_text
    try:
        # Recognize speech using Google Speech Recognition
        text = recognizer.recognize_google(audio_data, language='en-US')
        print(f"Recognized Text: {text}")

        # Translate text to Kannada using deep-translator
        translated_text = GoogleTranslator(source='en', target='kn').translate(text)
        print(f"Translated Text: {translated_text}")

        # Convert translated text to speech
        tts = gTTS(text=translated_text, lang='kn')
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_audio_file.name)

        return temp_audio_file.name

    except Exception as e:
        print("An error occurred in recognize_and_translate_audio:")
        traceback.print_exc()
        translated_text = ''
        return None

def play_translated_audio(audio_file):
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

def release_audio_file(audio_file):
    pygame.mixer.music.unload()
    os.remove(audio_file)

def audio_capture_thread():
    # List available devices
    print("Available audio input devices:")
    for i in range(audio.get_device_count()):
        device = audio.get_device_info_by_index(i)
        print(f"Device {i}: {device['name']}  (Input channels: {device['maxInputChannels']})")
    # You can specify input_device_index if needed

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    audio_frames = []
    print("Audio thread started.")
    while True:
        data = stream.read(CHUNK)
        audio_frames.append(data)

        # Implement logic to detect end of speech
        if len(audio_frames) >= int(RATE / CHUNK * 3):
            print("Processing audio data...")
            audio_data = sr.AudioData(b''.join(audio_frames), RATE, 2)
            audio_frames = []  # Reset audio frames before processing to prevent overlap
            audio_file = recognize_and_translate_audio(audio_data)
            if audio_file:
                print("Playing translated audio...")
                play_translated_audio(audio_file)
                while pygame.mixer.music.get_busy():
                    continue
                release_audio_file(audio_file)
            else:
                print("No audio file generated.")

def video_display_thread():
    global translated_text
    font = cv2.FONT_HERSHEY_SIMPLEX
    print("Video thread started.")
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Add the translated text as subtitles
        if translated_text:
            # Set up the text properties
            text = translated_text
            font_scale = 1
            color = (255, 255, 255)
            thickness = 2
            # Get the width and height of the text box
            (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
            # Set the text start position
            text_offset_x = 10
            text_offset_y = frame.shape[0] - 30
            # Make a background rectangle
            box_coords = ((text_offset_x - 5, text_offset_y + 5),
                          (text_offset_x + text_width + 5, text_offset_y - text_height - 5))
            cv2.rectangle(frame, box_coords[0], box_coords[1], (0, 0, 0), cv2.FILLED)
            # Put the text onto the frame
            cv2.putText(frame, text, (text_offset_x, text_offset_y), font,
                        font_scale, color, thickness, cv2.LINE_AA)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    video_capture.release()
    cv2.destroyAllWindows()
    audio.terminate()

# Start the audio capture thread
audio_thread = threading.Thread(target=audio_capture_thread)
audio_thread.daemon = True
audio_thread.start()

# Start the video display thread (main thread)
video_display_thread()