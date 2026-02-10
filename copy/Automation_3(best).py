# Import required libraries
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import os
import re
from duckduckgo_search import DDGS
import time
import pyautogui
import asyncio
from typing import List

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize AI client
client = Groq(api_key=GroqAPIKey)

# List to store chatbot messages
messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'Chatbot')}, You're a content writer."}]


# ---- 1. GOOGLE SEARCH ----

# ---- 1. SIMPLE GOOGLE SEARCH (Opens in browser) ----
def GoogleSearch(topic):
    """Open Google search results in a web browser."""
    search_url = f"https://www.google.com/search?q={topic}"
    webbrowser.open(search_url)
    return True

# ---- 2. ADVANCED GOOGLE SEARCH (Extracts and visits the first link) ----
def search_duckduckgo(query):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=1))
        if results:
            first_link = results[0]['href']
            print(f"📄 Title: {results[0]['title']}\n🔗 {first_link}\n\n{results[0]['body']}")
            webbrowser.open(first_link)
            return f"✅ Opened in browser: {first_link}"
    return "❌ No valid results found."

# ---- 3. AI CONTENT GENERATION ----
def Content(Topic):
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})  
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content  
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    ContentByAI = ContentWriterAI(f"Write a {Topic}")
    file_path = rf"C:\\Users\\prath\\OneDrive\\Desktop\\Jarvis\\Data\\contentwriter.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    subprocess.run(["notepad.exe", file_path])
    return True

# ---- 4. YOUTUBE FUNCTIONS ----
def YouTubeSearch(topic):
    url = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(url)
    print(f"🔍 Opened YouTube search results for: {topic}")
    return True

def PlayYoutube(query):
    print(f"▶️ Playing first YouTube result for: {query}")
    playonyt(query)
    return True

# ---- 5. APPLICATION CONTROL ----
def extract_links(html):
    if html is None:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    links = [a['href'].split("&")[0].replace("/url?q=", "") for a in soup.find_all('a', href=True) if "url?q=" in a['href']]
    return links

def OpenApp(app):
    try:
        print(f"🟢 Trying to open application: {app}")
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        print(f"🔍 Searching for {app} online...")
        html = search_duckduckgo(app)
        if html:
            links = extract_links(html)
            if links:
                print(f"🌐 Opening {links[0]}")
                webbrowser.open(links[0])
        return True

def CloseApp(app):
    if "chrome" in app:
        print("❌ Cannot close Chrome!")
        return False
    try:
        print(f"🔴 Closing application: {app}")
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        print("⚠️ Unable to close the application.")
        return False

# ---- 6. SYSTEM COMMANDS ----
def System(command):
    commands = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down"),
    }
    if command in commands:
        print(f"🔧 Executing command: {command}")
        commands[command]()
    return True


#------------------------------------------------------------------------------------------------#

import webbrowser
import time
import pyautogui
import os
import subprocess
import asyncio
from typing import List

# Define your contacts
CONTACTS = {
    "ayush mangela": "+919892207022".strip(),  # Remove extra spaces
    "mheet nmims": "+919969148543".strip()
}


# Paths to button images
VOICE_CALL_ICON_PATH = r"C:\Users\prath\OneDrive\Desktop\Jarvis\copy\voice_call_icon.png"
VIDEO_CALL_ICON_PATH = r"C:\Users\prath\OneDrive\Desktop\Jarvis\copy\video_call_icon.png"

# Set the Desktop path manually
DESKTOP_PATH = r"C:\Users\prath\OneDrive\Desktop"

def send_whatsapp_message(name, message):
    name = name.strip().lower()

    # Check for exact or partial match
    matched_contact = next((contact for contact in CONTACTS if name in contact), None)

    if matched_contact:
        phone_number = CONTACTS[matched_contact]
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
        webbrowser.open(whatsapp_url)
        time.sleep(10)  # Wait for WhatsApp Web

        for _ in range(15):
            pyautogui.press("enter")
            time.sleep(1)

        print(f"✅ WhatsApp message sent to {matched_contact}.")
        return True

    print(f"❌ Contact '{name}' not found.")
    return False


#-----------whatsup voice call-----------------------#

def whatsapp_voice_call(name):
    if name.lower() in CONTACTS:
        phone_number = CONTACTS[name.lower()]
        whatsapp_url = f"whatsapp://send?phone={phone_number}"
        webbrowser.open(whatsapp_url)
        time.sleep(8)
        if not os.path.exists(VOICE_CALL_ICON_PATH):
            return "❌ Missing voice call button image."
        call_button = pyautogui.locateCenterOnScreen(VOICE_CALL_ICON_PATH, confidence=0.8)
        if call_button:
            pyautogui.click(call_button)
            return f"✅ Voice call started with {name}."
        return "❌ Voice call button not detected."
    return "❌ Contact not found."

#----------whatsup video call-----------------#

def whatsapp_video_call(name):
    if name.lower() in CONTACTS:
        phone_number = CONTACTS[name.lower()]
        whatsapp_url = f"whatsapp://send?phone={phone_number}"
        webbrowser.open(whatsapp_url)
        time.sleep(8)
        if not os.path.exists(VIDEO_CALL_ICON_PATH):
            return "❌ Missing video call button image."
        video_button = pyautogui.locateCenterOnScreen(VIDEO_CALL_ICON_PATH, confidence=0.8)
        if video_button:
            pyautogui.click(video_button)
            return f"✅ Video call started with {name}."
        return "❌ Video call button not detected."
    return "❌ Contact not found."


#-------------find and open folder and files---------------------#

import os
import subprocess
import shutil
import webbrowser
import time
import asyncio
import requests
from bs4 import BeautifulSoup

DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

def duckduckgo_search_and_open(query):
    """Search DuckDuckGo and open the first valid result link in the default browser."""
    time.sleep(2)  # ✅ Delay to avoid rate-limiting
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if href.startswith("/l/?kh="):  # DuckDuckGo result links start differently
                    first_link = href.split("/l/?kh=")[1].split("&")[0]
                    print(f"✅ Opening: {first_link}")
                    webbrowser.open(first_link)
                    return

    except Exception as e:
        print(f"❌ DuckDuckGo search failed: {e}")
    
    print(f"🔍 No valid result found. Opening DuckDuckGo search page...")
    webbrowser.open(search_url)

import os
import subprocess
import shutil

DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

def open_with_suitable_app(file_path):
    """Open a file with a suitable application."""
    ext = os.path.splitext(file_path)[-1].lower()
    
    app_map = {
        ".py": "code",
        ".cpp": "code",
        ".java": "code",
        ".js": "code",
        ".html": "code",
        ".txt": "notepad",
        ".jpg": "mspaint",
        ".png": "mspaint",
        ".mp4": "vlc",
        ".mkv": "vlc",
    }

    if ext in app_map:
        subprocess.run([app_map[ext], file_path])
    else:
        os.startfile(file_path)  # Open with default app

def find_and_open(name):
    """Find and open a file, folder, or application from the desktop."""
    name = name.lower().strip()

    for root, dirs, files in os.walk(DESKTOP_PATH):  
        if name in dirs:
            folder_path = os.path.join(root, name)
            subprocess.run(["explorer", folder_path])
            return
        
        for file in files:
            if file.lower() == name or file.lower().startswith(name):
                file_path = os.path.join(root, file)
                open_with_suitable_app(file_path)
                return

    for ext in [".lnk", ".exe"]:
        app_path = os.path.join(DESKTOP_PATH, name + ext)
        if os.path.exists(app_path):
            os.startfile(app_path)
            return

    app_exe = shutil.which(name)
    if app_exe:
        subprocess.run([app_exe], shell=True)
        return

    print(f"❌ Could not find '{name}' on the desktop.")

# if __name__ == "__main__":
#     find_and_open("clap.py") 




# ---- 7. ASYNCHRONOUS COMMAND HANDLER ----
async def TranslateAndExecute(commands: List[str]):
    funcs = []
    for command in commands:
        if command.startswith("open "):
            funcs.append(asyncio.to_thread(find_and_open, command.removeprefix("open ")))
        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))
        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))
        elif command.startswith("content "):
            topic = command.removeprefix("content ")
            result = await asyncio.to_thread(Content, topic)
            yield result
        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))
        elif command.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")))
        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))
        elif command.startswith("whatsapp message "):
            parts = command.removeprefix("whatsapp message ").split(" ", 1)
            if len(parts) == 2:
                funcs.append(asyncio.to_thread(send_whatsapp_message, parts[0], parts[1]))
        elif command.startswith("whatsapp call "):
            funcs.append(asyncio.to_thread(whatsapp_voice_call, command.removeprefix("whatsapp call ")))
        elif command.startswith("whatsapp video call "):
            funcs.append(asyncio.to_thread(whatsapp_video_call, command.removeprefix("whatsapp video call ")))
        else:
            print(f"No Function Found for {command}")
    results = await asyncio.gather(*funcs)
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

# ---- 8. AUTOMATION FUNCTION ----
async def Automation(commands: List[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True



# ---- 9. MAIN EXECUTION ----
if __name__ == "__main__":
    asyncio.run(Automation([
        #  "google search pratham pednekar", 
        #  "search future of ai", 
        #  "play AI revolution on YouTube", 
        #  "open notepad", 
        #  "open Visual Studio Code" 
        #  "content AI impact on jobs", 
        #  "system mute", 
        #  "whatsapp message ayush mangela Hello!",  
        #  "whatsapp call mheet nmims"
       # "whatsapp video call ayush mangela"
    ]))


# # ---- 9. MAIN EXECUTION ----
# if __name__ == "__main__":
#     asyncio.run(Automation([
#         "google search pratham pednekar", 
#         " future of ai", 
#         "play AI revolution on YouTube", 
#         "open notepad", 
#         "open spotify", 
#         "content AI impact on jobs", 
#         "system mute", 
#         "whatsapp message ayush mangela Hello!", 
#         "whatsapp call mheet nmims", 
#         "whatsapp video call ayush mangela"
#     ]))

# if __name__ == "__main__":
#     find_and_open("open spotify")  # ✅ Opens Spotify 
#     find_and_open("search future of ai")  # ✅ Searches Google & opens the first result
#     find_and_open("search latest AI trends") 

