#Till now Best created but not the same as kaushik(youtube)
import speech_recognition as sr
import os
import mtranslate as mt
import time

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
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  
        recognizer.energy_threshold = 40  # More sensitive to low volume speech
        recognizer.pause_threshold = 1.2  # Allows 2.5 seconds of thinking time
        recognizer.non_speaking_duration = 1.2  # Finalize text after 3 seconds of silence
        recognizer.dynamic_energy_threshold = True  

        while True:
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=20)  
                time.sleep(0.1)  # Wait 0.1 seconds after speech ends
                text = recognizer.recognize_google(audio)
                # Apply translator + query modifier
                text = UniversalTranslator(text)
                text = QueryModifier(text)
                print(text)  # Only prints spoken text
            except sr.UnknownValueError:
                pass  # Ignore unrecognized speech
            except sr.WaitTimeoutError:
                pass  # Ignore timeout errors
            except sr.RequestError:
                pass  # Ignore API errors

# Start Speech Recognition
SpeechRecognition()