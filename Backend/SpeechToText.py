import speech_recognition as sr
import os
import mtranslate as mt
import time
from Backend.TextToSpeech import StopSpeech  

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TempDirPath = os.path.join(PROJECT_ROOT, "Frontend", "Files")

def QueryModifier(Query):
    new_query = Query.lower().strip()
    question_words = ["how", "what", "who", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    if any(word + " " in new_query for word in question_words):
        new_query += "?" if new_query[-1] not in ['.', '?', '!'] else ""
    else:
        new_query += "." if new_query[-1] not in ['.', '?', '!'] else ""
    return new_query.capitalize()

def UniversalTranslator(Text):
    return mt.translate(Text, "en", "auto").capitalize()

def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}\Status.data", "w", encoding='utf-8') as file:
        file.write(Status)

def SpeechRecognition():
    """Recognize one sentence of speech and return it."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        recognizer.energy_threshold = 40
        recognizer.pause_threshold = 1.2
        recognizer.non_speaking_duration = 1.2
        recognizer.dynamic_energy_threshold = True

        try:
            print("[🎤 Listening for speech...]")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=20)
            text = recognizer.recognize_google(audio)
            
            SetAssistantStatus("Translating ...")
            text = UniversalTranslator(text)
            text = QueryModifier(text)
            print(f"[✅ Recognized]: {text}")

            # ✅ Check for voice stop commands
            if "stop reading" in text.lower() or "stop speaking" in text.lower():
                print("[🛑 Voice Command] Stop Reading detected!")
                StopSpeech()
                return ""  # return empty to avoid triggering any further action

            return text

        except sr.UnknownValueError:
            return ""
        except sr.WaitTimeoutError:
            return ""
        except sr.RequestError:
            return ""
        except Exception as e:
            print(f"[STT Error] {e}")
            return ""

# ✅ Test
if __name__ == "__main__":
    print(SpeechRecognition())




# import speech_recognition as sr
# import os
# import mtranslate as mt
# import time

# current_dir = os.getcwd()
# TempDirPath = rf"{current_dir}/Frontend/Files"

# def QueryModifier(Query):
#     new_query = Query.lower().strip()
#     question_words = ["how", "what", "who", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
#     if any(word + " " in new_query for word in question_words):
#         new_query += "?" if new_query[-1] not in ['.', '?', '!'] else ""
#     else:
#         new_query += "." if new_query[-1] not in ['.', '?', '!'] else ""
#     return new_query.capitalize()

# def UniversalTranslator(Text):
#     return mt.translate(Text, "en", "auto").capitalize()

# def SpeechRecognition():
#     """Recognize one sentence of speech and return it."""
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         recognizer.adjust_for_ambient_noise(source, duration=0.5)
#         recognizer.energy_threshold = 40
#         recognizer.pause_threshold = 1.2
#         recognizer.non_speaking_duration = 1.2
#         recognizer.dynamic_energy_threshold = True

#         try:
#             print("[🎤 Listening for speech...]")
#             audio = recognizer.listen(source, timeout=10, phrase_time_limit=20)
#             text = recognizer.recognize_google(audio)
#             text = UniversalTranslator(text)
#             text = QueryModifier(text)
#             print(f"[✅ Recognized]: {text}")
#             return text
#         except sr.UnknownValueError:
#             return ""
#         except sr.WaitTimeoutError:
#             return ""
#         except sr.RequestError:
#             return ""
#         except Exception as e:
#             print(f"[STT Error] {e}")
#             return ""

# # ✅ Remove the infinite loop here (important!)
# if __name__ == "__main__":
#     print(SpeechRecognition())
