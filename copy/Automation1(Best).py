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

def search_duckduckgo(query):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=1))
        if results:
            first_link = results[0]['href']
            print(f"📄 Title: {results[0]['title']}\n🔗 {first_link}\n\n{results[0]['body']}")

            # Open first result in Chrome
            webbrowser.open(first_link)

            return f"✅ Opened in browser: {first_link}"

    return "❌ No valid results found."

# Run the function
#print(search_duckduckgo("Future of AI"))

## ---- 2. AI CONTENT GENERATION ----

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

    # Generate AI-based content dynamically based on the provided topic
    ContentByAI = ContentWriterAI(f"Write a {Topic}")

    # Define a fixed file path for all generated content
    file_path = rf"C:\Users\prath\OneDrive\Desktop\Jarvis\Data\contentwriter.txt"

    # Save the generated content to the fixed file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    # Open the file in Notepad
    subprocess.run(["notepad.exe", file_path])

    return True

#if __name__ == "__main__":
    #Content("write a complaint on my son to not giving me house property")


# ---- 3. YOUTUBE FUNCTIONS ----

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


# ---- 4. APPLICATION CONTROL ----

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


# CloseApp("notepad")  # Closes Notepad
# CloseApp("Spotify")  # Closes Spotify (if running)



# ---- 5. SYSTEM COMMANDS ----
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









import webbrowser
import time
import pyautogui
import os
import subprocess
import asyncio

# Define your contacts
CONTACTS = {
    "ayush mangela": "+919892207022",
    "mheet nmims": "+919969148543"
}

# Paths to button images
VOICE_CALL_ICON_PATH = r"C:\Users\prath\OneDrive\Desktop\Jarvis\copy\voice_call_icon.png"
VIDEO_CALL_ICON_PATH = r"C:\Users\prath\OneDrive\Desktop\Jarvis\copy\video_call_icon.png"

# Set Desktop Path
DESKTOP_PATH = r"C:\Users\prath\OneDrive\Desktop"


async def send_whatsapp_message(name, message):
    """Send a WhatsApp message instantly."""
    if name.lower() in CONTACTS:
        phone_number = CONTACTS[name.lower()]
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
        
        webbrowser.open(whatsapp_url)  # Open WhatsApp Web
        await asyncio.sleep(5)  # Wait for the page to load
        
        for _ in range(10):  # Try sending message
            pyautogui.press("enter")
            await asyncio.sleep(1)

        print(f"✅ Message sent to {name}: {message}")
    else:
        print("❌ Contact not found.")


async def whatsapp_voice_call(name):
    """Initiate a WhatsApp voice call using WhatsApp Desktop."""
    if name.lower() in CONTACTS:
        phone_number = CONTACTS[name.lower()]
        whatsapp_url = f"whatsapp://send?phone={phone_number}"
        webbrowser.open(whatsapp_url)
        await asyncio.sleep(8)  # Wait for WhatsApp Desktop to load

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


async def whatsapp_video_call(name):
    """Initiate a WhatsApp video call using WhatsApp Desktop."""
    if name.lower() in CONTACTS:
        phone_number = CONTACTS[name.lower()]
        whatsapp_url = f"whatsapp://send?phone={phone_number}"
        webbrowser.open(whatsapp_url)
        await asyncio.sleep(8)

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


async def find_and_open(name):
    """Find and open a file/folder/application on Desktop."""
    for root, dirs, files in os.walk(DESKTOP_PATH):  
        if name in dirs:
            subprocess.run(["explorer", os.path.join(root, name)])  # Open folder
            return

        for file in files:
            if file.lower() == name.lower():
                open_with_suitable_app(os.path.join(root, file))
                return

    app_path = os.path.join(DESKTOP_PATH, name + ".lnk")
    exe_path = os.path.join(DESKTOP_PATH, name + ".exe")
    if os.path.exists(app_path) or os.path.exists(exe_path):
        subprocess.run([app_path if os.path.exists(app_path) else exe_path], shell=True)
        return

    print(f"❌ File, folder, or app '{name}' not found.")


def open_with_suitable_app(file_path):
    """Open a file in the most suitable application."""
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


async def main():
    """Run all tasks asynchronously."""
    tasks = [
        # send_whatsapp_message("ayush mangela", "Hello, I am Jarvis!"),
        # whatsapp_voice_call("mheet nmims"),
        # whatsapp_video_call("ayush mangela"),
        # find_and_open("clap.py")
    ]
    await asyncio.gather(*tasks)


# Run the script
if __name__ == "__main__":
    asyncio.run(main())












#----without async whastup ----#
import webbrowser
import time
import pyautogui

# Define your contacts
CONTACTS = {
     "ayush mangela": "+919892207022",
     "mheet nmims": "+919969148543"
}

def send_whatsapp_message(name, message):
    """Send a WhatsApp message instantly with optimized speed."""
    if name.lower() in CONTACTS:
        phone_number = CONTACTS[name.lower()]
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
        
        webbrowser.open(whatsapp_url)  # Open WhatsApp Web
        
        time.sleep(5)  # Reduced wait time
        
        # Ensure WhatsApp Web is loaded before pressing enter
        for _ in range(10):  # Check for 10 iterations (max 10 seconds)
            pyautogui.press("enter")
            time.sleep(1)  # Small delay to confirm message is sent
        
        print(f"✅ Message sent to {name}: {message}")
        return f"✅ WhatsApp message sent to {name}."
    
    else:
        return "❌ Contact not found."

# Example usage
#send_whatsapp_message("Ayush Mangela", "Hello I am jarvis, Fuck u!")

#----Phone call----#

import webbrowser
import time
import pyautogui
import os

# Define your contacts
CONTACTS = {
    "ayush mangela": "+919892207022",
    "mheet nmims": "+919969148543"
}

# Paths to button images
VOICE_CALL_ICON_PATH = r"C:\Users\prath\OneDrive\Desktop\Jarvis\copy\voice_call_icon.png"
VIDEO_CALL_ICON_PATH = r"C:\Users\prath\OneDrive\Desktop\Jarvis\copy\video_call_icon.png"

def whatsapp_voice_call(name):
    """Initiate a WhatsApp voice call using WhatsApp Desktop."""
    if name.lower() in CONTACTS:
        phone_number = CONTACTS[name.lower()]
        
        # Open WhatsApp chat in the desktop app
        whatsapp_url = f"whatsapp://send?phone={phone_number}"
        webbrowser.open(whatsapp_url)
        time.sleep(8)  # Wait for WhatsApp Desktop to load

        # Ensure the voice call icon exists
        if not os.path.exists(VOICE_CALL_ICON_PATH):
            print("❌ Error: 'voice_call_icon.png' not found! Ensure it's in the correct path.")
            return "❌ Missing voice call button image."

        # Locate and click the voice call button
        call_button = pyautogui.locateCenterOnScreen(VOICE_CALL_ICON_PATH, confidence=0.8)
        
        if call_button:
            pyautogui.click(call_button)
            print(f"📞 Voice calling {name} on WhatsApp...")
            return f"✅ Voice call started with {name}."
        else:
            print("❌ Could not find the voice call button. Ensure WhatsApp is open and visible.")
            return "❌ Voice call button not detected."

    else:
        return "❌ Contact not found."
    
#whatsapp_voice_call("ayush mangela")

def whatsapp_video_call(name):
    """Initiate a WhatsApp video call using WhatsApp Desktop."""
    if name.lower() in CONTACTS:
        phone_number = CONTACTS[name.lower()]
        
        # Open WhatsApp chat in the desktop app
        whatsapp_url = f"whatsapp://send?phone={phone_number}"
        webbrowser.open(whatsapp_url)
        time.sleep(8)  # Wait for WhatsApp Desktop to load

        # Ensure the video call icon exists
        if not os.path.exists(VIDEO_CALL_ICON_PATH):
            print("❌ Error: 'video_call_icon.png' not found! Ensure it's in the correct path.")
            return "❌ Missing video call button image."

        # Locate and click the video call button
        video_button = pyautogui.locateCenterOnScreen(VIDEO_CALL_ICON_PATH, confidence=0.8)
        
        if video_button:
            pyautogui.click(video_button)
            print(f"📹 Video calling {name} on WhatsApp...")
            return f"✅ Video call started with {name}."
        else:
            print("❌ Could not find the video call button. Ensure WhatsApp is open and visible.")
            return "❌ Video call button not detected."

    else:
        return "❌ Contact not found."

#whatsapp_video_call("mheet nmims")


#----Open file folder----#

import os
import subprocess

# Set the Desktop path manually
DESKTOP_PATH = r"C:\Users\prath\OneDrive\Desktop"

def find_and_open(name):
    for root, dirs, files in os.walk(DESKTOP_PATH):  
        # Check if it's a folder
        if name in dirs:
            folder_path = os.path.join(root, name)
            subprocess.run(["explorer", folder_path])  # Open folder in Explorer
            return
        
        # Check if it's a file
        for file in files:
            if file.lower() == name.lower():  # Exact match (ignores case)
                file_path = os.path.join(root, file)
                open_with_suitable_app(file_path)
                return

    # Check if it's an application (shortcut or .exe) on the Desktop
    app_path = os.path.join(DESKTOP_PATH, name + ".lnk")  # Look for shortcuts (.lnk)
    exe_path = os.path.join(DESKTOP_PATH, name + ".exe")  # Look for direct executables
    if os.path.exists(app_path) or os.path.exists(exe_path):
        subprocess.run([app_path if os.path.exists(app_path) else exe_path], shell=True)
        return

    print(f"File, folder, or app '{name}' not found on Desktop.")

def open_with_suitable_app(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    
    if ext in [".py", ".cpp", ".java", ".js", ".html"]:
        subprocess.run([r"C:\Users\prath\AppData\Local\Programs\Microsoft VS Code\Code.exe", file_path])  # Open in VS Code
    elif ext in [".txt"]:
        subprocess.run(["notepad", file_path])  # Open in Notepad
    elif ext in [".jpg", ".png", ".jpeg", ".gif", ".bmp", ".webp"]:
        subprocess.run(["mspaint", file_path])  # Open images in Paint
    elif ext in [".mp4", ".mkv", ".avi", ".mov", ".flv"]:
        subprocess.run(["vlc", file_path])  # Open videos in VLC (make sure VLC is installed)
    else:
        os.startfile(file_path)  # Open with the default app

#find_and_open("clap.py")  # Opens "clap.py" if it's on the Desktop
#find_and_open("David")  # Opens a folder
#find_and_open("Visual studio Code")  # Opens the VS Code app if it has a shortcut on Desktop





























# # Asynchronous function to translate and execute user commands.
# async def TranslateAndExecute(commands: List[str]):

#     funcs = []  # List to store asynchronous tasks.

#     for command in commands:

#         if command.startswith("open "):  # Handle "open" commands.
#             if "open it" in command:  # Ignore "open it" commands.
#                 pass
#             if "open file" == command:  # Ignore "open file" commands.
#                 pass
#             else:
#                 fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))  # Schedule app opening.
#                 funcs.append(fun)

#         elif command.startswith("general "):  # Placeholder for general commands.
#             pass

#         elif command.startswith("realtime "):  # Placeholder for real-time commands.
#             pass

#         elif command.startswith("close "):  # Handle "close" commands.
#             fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))  # Schedule app closing.
#             funcs.append(fun)

#         elif command.startswith("play "):  # Handle "play" commands.
#             fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))  # Schedule YouTube playback.
#             funcs.append(fun)

#         elif command.startswith("content "):  # Handle "content" commands.
#             fun = asyncio.to_thread(Content, command.removeprefix("content "))  # Schedule content creation.
#             funcs.append(fun)

#         elif command.startswith("google search "):  # Handle Google search commands.
#             fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))  # Schedule Google search.
#             funcs.append(fun)
#         elif command.startswith("youtube search "):  # Handle YouTube search commands.
#             fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))  # Schedule YouTube search.
#             funcs.append(fun)

#         elif command.startswith("system "):  # Handle system commands.
#             fun = asyncio.to_thread(System, command.removeprefix("system "))  # Schedule system command.
#             funcs.append(fun)

#         else:
#             print(f"No Function Found. For {command}")  # Print an error for unrecognized commands.

#         results = await asyncio.gather(*funcs)  # Execute all tasks concurrently.

#         for result in results:  # Process the results.
#             if isinstance(result, str):
#                 yield result
#             else:   
#                 yield result


# # Asynchronous function to automate command execution.
# async def Automation(commands: list[str]):

#     async for result in TranslateAndExecute(commands):  # Translate and execute commands.
#         pass

#     return True  # Indicate success.


# if __name__ == "__main__":
#     asyncio.run(Automation(["open facebook", "play afsanay", "content: song for me"]))

