from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")  # Default to English if not set

# Define Speech Recognition HTML
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = 'en';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent = transcript;  // Overwrite instead of appending
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Save the HTML file
html_path = os.path.join(os.getcwd(), "Data", "Voice.html")
os.makedirs(os.path.dirname(html_path), exist_ok=True)
with open(html_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")  # Keeps it running in the background

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def SpeechRecognition():
    """Start speech recognition and continuously print recognized speech."""
    driver.get("file:///" + html_path)

    # Click start button
    driver.find_element(By.ID, "start").click()
    
    last_text = ""  # Store last recognized text to avoid duplicates

    try:
        while True:
            # Wait for speech to be recognized
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "output")))
            recognized_text = driver.find_element(By.ID, "output").text.strip()

            if recognized_text and recognized_text != last_text:
                print("Recognized:", recognized_text)
                last_text = recognized_text  # Update last recognized text

    except KeyboardInterrupt:
        # Stop recognition on user interruption (Ctrl+C)
        driver.find_element(By.ID, "end").click()
        print("\nSpeech recognition stopped.")
        driver.quit()

# Run Speech Recognition
SpeechRecognition()
