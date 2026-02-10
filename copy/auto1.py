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
import pywhatkit


# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Define user-agent for web scraping
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize AI client
client = Groq(api_key=GroqAPIKey)

# List to store chatbot messages
messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'Chatbot')}, You're a content writer."}]


# ---- 1. GOOGLE SEARCH ----
import requests
import webbrowser
from bs4 import BeautifulSoup

# Define user-agent for web scraping
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'



# ---- 1. SIMPLE GOOGLE SEARCH (Opens in browser) ----
def GoogleSearch(topic):
    """Open Google search results in a web browser."""
    search_url = f"https://www.google.com/search?q={topic}"
    webbrowser.open(search_url)
    return True

#GoogleSearch("AI chatbot")  # Example usage



# ---- 2. ADVANCED GOOGLE SEARCH (Extracts and visits the first link) ----

async def search_duckduckgo(query: str):
    await asyncio.sleep(2)  # Add a short delay to prevent rate limiting
    with DDGS() as ddgs:
        try:
            results = list(ddgs.text(query, max_results=1))
            if results:
                first_link = results[0]['href']
                print(f"📄 Title: {results[0]['title']}\n🔗 {first_link}\n\n{results[0]['body']}")
                webbrowser.open(first_link)
                return f"✅ Opened in browser: {first_link}"
        except Exception as e:
            return f"❌ DuckDuckGo search failed: {str(e)}"
    return "❌ No valid results found."


#asyncio.run(search_duckduckgo("Future of AI"))
#search_duckduckgo("Future of AI")




## ---- 3. AI CONTENT GENERATION ----

import datetime

def Content(Topic):
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})  
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
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

    # Generate AI-based content dynamically
    ContentByAI = ContentWriterAI(f"Write a {Topic}")

    # Create a unique file name using timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{Topic[:30].strip().replace(' ', '_')}_{timestamp}.txt"

    # Define full file path
    file_path = rf"C:\Users\prath\OneDrive\Desktop\Jarvis\Data\AI_Content_History\{file_name}"

    # Save content to the new file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    # Open the file in Notepad
    subprocess.run(["notepad.exe", file_path])

    return True

#Content("Write a short story about a robot who wanted to become a poet.")


# ---- 4. YOUTUBE FUNCTIONS ----

def YouTubeSearch(topic):
    """Search for a topic on YouTube (opens search results page)."""
    url = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(url)
    print(f"🔍 Opened YouTube search results for: {topic}")
    return True

#YouTubeSearch("AI advancements 2024")  # Opens search results

def PlayYoutube(query):
    """Search for a YouTube video and play the first result."""
    print(f"▶️ Playing first YouTube result for: {query}")
    playonyt(query)  # This automatically plays the first video
    return True

#PlayYoutube("AI advancements 2024")  # Plays the first video



# ---- 5. APPLICATION CONTROL ----

def extract_links(html):
    """Extract links from Google search results."""
    if html is None:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    links = [a['href'].split("&")[0].replace("/url?q=", "") for a in soup.find_all('a', href=True) if "url?q=" in a['href']]
    return links

def OpenApp(app):
    """Open an application or relevant webpage."""
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

#OpenApp("notepad")  # Tries to open Notepad
#OpenApp("Spotify")  # Tries to open Spotify; if not found, searches online

def CloseApp(app):
    """Close an application."""
    if "chrome" in app:  # Prevent accidental closing of Chrome
        print("❌ Cannot close Chrome!")
        return False
    try:
        print(f"🔴 Closing application: {app}")
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        print("⚠️ Unable to close the application.")
        return False


#CloseApp("notepad")  # Closes Notepad
#CloseApp("Spotify")  # Closes Spotify (if running)

#-----------6. opens files with extensions---------#


import os
import subprocess

#Get Desktop Path
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

def open_with_suitable_app(file_name):
    """Open a file from Desktop in the most suitable application."""
    file_path = os.path.join(DESKTOP_PATH, file_name)  # Assume file is on Desktop

    if not os.path.exists(file_path):
        print(f"❌ File '{file_name}' not found on Desktop.")
        return

    ext = os.path.splitext(file_path)[-1].lower()
    
    if ext in [".py", ".cpp", ".java", ".js", ".html"]:
        subprocess.run([r"C:\Users\prath\AppData\Local\Programs\Microsoft VS Code\Code.exe", file_path])
    elif ext in [".txt"]:
        subprocess.run(["notepad", file_path])
    elif ext in [".jpg", ".png", ".jpeg", ".gif", ".bmp", ".webp"]:
        subprocess.run(["mspaint", file_path])
    elif ext in [".mp4", ".mkv", ".avi", ".mov", ".flv"]:
        subprocess.run(["vlc", file_path])
    else:
        os.startfile(file_path)

#✅**How to call this function:**
#open_with_suitable_app("Clap.py")  # This will open Clap.py from Desktop
#open_with_suitable_app("example.txt")  # Opens example.txt from Desktop
#open_with_suitable_app("photo.jpg")  # Opens photo.jpg from Desktop




# ---- 7. SYSTEM COMMANDS ----#
def System(command):
    """Execute system-level commands such as mute, unmute, volume up, and volume down."""
    
    # Dictionary mapping commands to corresponding keyboard actions
    commands = {
        "mute": lambda: keyboard.press_and_release("volume mute"),  # Mutes system volume
        "unmute": lambda: keyboard.press_and_release("volume mute"),  # Unmutes (same as mute toggle)
        "volume up": lambda: keyboard.press_and_release("volume up"),  # Increases volume
        "volume down": lambda: keyboard.press_and_release("volume down"),  # Decreases volume
    }
    
    # Execute command if found in dictionary
    if command in commands:
        print(f"🔧 Executing command: {command}")  # Debugging message
        commands[command]()  # Run the associated function
    
    return True  # Always return True

# 🔹 Example Usage
#System("mute")  # Mutes system volume
#System("volume up")  # Increases volume
#System("volume down")  # Decreases volume
#System("unmute")  # Unmutes system volume


#-----------------8. whatsup message--------------#


import webbrowser
import time
import pyautogui

# Original names
RAW_CONTACTS = {
    "Ayush Mangela": "+919892207022",
    "Mheet Nmims": "+919969148543",
    "Kaustubh Guruji": "+919112696177"
}

# Case-insensitive lookup
CONTACTS = {name.lower(): phone for name, phone in RAW_CONTACTS.items()}

def send_whatsapp_message(name, message):
    """Send a WhatsApp message instantly."""
    key = name.lower()
    if key in CONTACTS:
        phone_number = CONTACTS[key]
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
        
        webbrowser.open(whatsapp_url)
        time.sleep(5)
        
        for _ in range(10):
            pyautogui.press("enter")
            time.sleep(5)

        print(f"✅ Message sent to {name}: {message}")
    else:
        print("❌ Contact not found.")

# Test call
#send_whatsapp_message("ayush mangela", "How are you? nigga")

#-----------------9. whatsup voice call--------------#


import os

VOICE_CALL_ICON_PATH = r"C:\Users\prath\OneDrive\Desktop\Jarvis\copy\voice_call_icon.png"

def whatsapp_voice_call(name):
    """Initiate a WhatsApp voice call using WhatsApp Desktop."""
    if name.lower() in CONTACTS:
        phone_number = CONTACTS[name.lower()]
        whatsapp_url = f"whatsapp://send?phone={phone_number}"

        webbrowser.open(whatsapp_url)
        time.sleep(8)  # Wait for WhatsApp Desktop to load

        if not os.path.exists(VOICE_CALL_ICON_PATH):
            print("❌ Error: 'voice_call_icon.png' not found!")
            return

        call_button = pyautogui.locateCenterOnScreen(VOICE_CALL_ICON_PATH, confidence=0.8)
        if call_button:
            pyautogui.click(call_button)
            print(f"📞 Voice calling {name} on WhatsApp...")
        else:
            print("❌ Voice call button not detected.")
    else:
        print("❌ Contact not found.")

# ✅ **How to call this function:**
#whatsapp_voice_call("mheet nmims")

#-----------------10. whatsup video call--------------#

VIDEO_CALL_ICON_PATH = r"C:\Users\prath\OneDrive\Desktop\Jarvis\copy\video_call_icon.png"

def whatsapp_video_call(name):
    """Initiate a WhatsApp video call using WhatsApp Desktop."""
    if name.lower() in CONTACTS:
        phone_number = CONTACTS[name.lower()]
        whatsapp_url = f"whatsapp://send?phone={phone_number}"
        webbrowser.open(whatsapp_url)
        time.sleep(8)

        if not os.path.exists(VIDEO_CALL_ICON_PATH):
            print("❌ Error: 'video_call_icon.png' not found!")
            return

        video_button = pyautogui.locateCenterOnScreen(VIDEO_CALL_ICON_PATH, confidence=0.8)
        if video_button:
            pyautogui.click(video_button)
            print(f"📹 Video calling {name} on WhatsApp...")
        else:
            print("❌ Video call button not detected.")
    else:
        print("❌ Contact not found.")

# ✅ **How to call this function:**
# whatsapp_video_call("ayush mangela")

#-----------------------------------11. Open Spotify --------------------------------------------------

import subprocess
import time
import pyautogui

def play_song_on_spotify(song_name):
    # Step 1: Open Spotify App
    try:
        subprocess.Popen(["spotify"])  # Works if 'spotify' is in PATH
        print("🎵 Opening Spotify app...")
        time.sleep(5)  # Wait for app to open

        # Step 2: Press Ctrl+L to focus the search bar
        pyautogui.hotkey("ctrl", "l")
        time.sleep(1)

        # Step 3: Type the song name
        pyautogui.write(song_name, interval=0.1)
        time.sleep(1)

        # Step 4: Press Enter to search
        pyautogui.press("enter")
        time.sleep(3)

        # Step 5: Press Tab a few times to reach song list, then Enter
        for _ in range(10):
            pyautogui.press("tab")
            time.sleep(0.1)

        pyautogui.press("enter")
        print(f"✅ Playing: {song_name}")

    except Exception as e:
        print(f"❌ Failed to open or control Spotify: {e}")

# 🔹 Example usage
#play_song_on_spotify("Let Her Go")


#------------------------------------------------------------------------------------------------------


async def TranslateAndExecute(commands: List[str]):
    funcs = []
    for command in commands:
        if command.startswith("message "):
            rest = command.removeprefix("message ").strip().lower()

            # Match full contact name from CONTACTS
            for contact in CONTACTS.keys():
                if rest.startswith(contact):
                    name = contact
                    message = rest[len(contact):].strip()
                    funcs.append(asyncio.to_thread(send_whatsapp_message, name, message))
                    break
            else:
                print(f"❌ No contact match found in: '{rest}'")
        elif command.startswith("voice call "):
            name = command.removeprefix("voice call ").strip()
            funcs.append(asyncio.to_thread(whatsapp_voice_call, name))
        elif command.startswith("video call "):
            name = command.removeprefix("video call ").strip()
            funcs.append(asyncio.to_thread(whatsapp_video_call, name))
        elif command.startswith("duckduckgo search "):
            funcs.append(asyncio.create_task(search_duckduckgo(command.removeprefix("duckduckgo search "))))
        elif command.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))
        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))
        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))
        elif command.startswith("content "):
            topic = command.removeprefix("content ")
            result = await asyncio.to_thread(Content, topic)
            yield result
        # elif command.startswith("file open "):
        #     funcs.append(asyncio.to_thread(open_with_suitable_app, command.removeprefix("file open ")))
        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))
        elif command.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")))
        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))
        elif command.startswith("spotify play "):
            funcs.append(asyncio.to_thread(play_song_on_spotify, command.removeprefix("spotify play ")))
        else:
            print(f"No Function Found. For {command}")
    
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
    if __name__ == "__main__":
        asyncio.run(Automation([
            #"google search pratham pednekar",
            #"youtube search pratham pednekar", 
            #"duckduckgo search Future of AI" 
            #"play AI revolution on youtube", 
            #"open visual studio code"
            #"open spotify" 
            #"content AI impact on jobs", 
            # "system mute"
            #"message ayush mangela Hello, I am Jarvis!",
            #"spotify play let her go",
            #"voice call Kaustubh guruji",
            #"video call ayush mangela",
        ]))
