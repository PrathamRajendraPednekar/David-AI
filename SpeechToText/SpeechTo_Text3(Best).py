import speech_recognition as sr

def real_time_speech_to_text():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
        recognizer.pause_threshold = 1.2  # Waits 1 second before finalizing speech

        while True:
            try:
                audio = recognizer.listen(source, timeout=None)  # Capture speech
                text = recognizer.recognize_google(audio)  # Convert speech to text
                print(text)  # Print only the recognized speech

            except (sr.UnknownValueError, sr.RequestError):
                pass  # Ignore errors silently

            except KeyboardInterrupt:
                break  # Stop when Ctrl+C is pressed

real_time_speech_to_text()
