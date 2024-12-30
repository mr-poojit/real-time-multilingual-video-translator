import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import tempfile
import os

recognizer = sr.Recognizer()
translator = Translator()

def recognize_and_translate_audio(audio_data):
    try:
        text = recognizer.recognize_google(audio_data, language='en-US')
        print(f"Recognized Text: {text}")

        # Translate text to Kannada
        translated = translator.translate(text, src='en', dest='kn')
        print(f"Translated Text: {translated.text}")

        tts = gTTS(text=translated.text, lang='kn')
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_audio_file.name)

        return temp_audio_file.name

    except Exception as e:
        print(f"Error: {e}")
        return None