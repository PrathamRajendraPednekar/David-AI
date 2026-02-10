#Till now Best created but not the same as kaushik(youtube)
import speech_recognition as sr
import os
import mtranslate as mt
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Frontend.GUI import GetMicrophoneStatus


# Get the current working directory
current_dir = os.getcwd()

# Define the path for temporary files
TempDirPath = rf"{current_dir}/Frontend/Files"

# Function to modify query format
def QueryModifier(Query):
    new_query = Query.lower().strip()
    question_words = ["how", "what", "who", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        new_query += "?" if new_query[-1] not in ['.', '?', '!'] else ""
    else:
        new_query += "." if new_query[-1] not in ['.', '?', '!'] else ""

    return new_query.capitalize()

# Function to translate text
def UniversalTranslator(Text):
    return mt.translate(Text, "en", "auto").capitalize()

# Improved Speech Recognition Function
def SpeechRecognition():
    mic_status = GetMicrophoneStatus()
    print("🎛️ Microphone status:", mic_status)  # <-- Debug print

    # Allow "True", "true", or actual boolean True
    if str(mic_status).lower() != "true":
        return "none"

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        recognizer.energy_threshold = 40
        recognizer.pause_threshold = 1.2
        recognizer.non_speaking_duration = 1.2
        recognizer.dynamic_energy_threshold = True

        try:
            print("🎤 Listening...")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            text = recognizer.recognize_google(audio)
            print("🗣️ Recognized:", text)
            return text

        except sr.UnknownValueError:
            if GetMicrophoneStatus() == "True":
                return "I didn’t catch that."
            return "none"

        except sr.WaitTimeoutError:
            if GetMicrophoneStatus() == "True":
                return "Listening timed out."
            return "none"

        except sr.RequestError:
            if GetMicrophoneStatus() == "True":
                return "Speech recognition failed."
            return "none"


# Start Speech Recognition
result = SpeechRecognition()
print("Result from SpeechRecognition:", result)