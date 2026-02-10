import pyautogui
import os
import time

# 🔁 Adjust this to either voice or video icon path
ICON_PATH = r"C:\Users\prath\OneDrive\Desktop\Jarvis\Backend\voice_call_icon.png"

# 🕓 Wait a few seconds so you can open WhatsApp
print("📷 You have 5 seconds to switch to WhatsApp...")
time.sleep(5)

if not os.path.exists(ICON_PATH):
    print("❌ Image file not found at:", ICON_PATH)
    exit()

print("🔍 Trying to locate the call button...")
location = pyautogui.locateCenterOnScreen(ICON_PATH, confidence=0.8)

if location:
    print(f"✅ Found icon at: {location}")
    pyautogui.moveTo(location)
    pyautogui.click()
else:
    print("❌ Could not detect icon. Try recapturing the screenshot.")
