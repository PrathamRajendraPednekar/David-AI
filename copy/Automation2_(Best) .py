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

# ---- 7. ASYNCHRONOUS COMMAND HANDLER ----
async def TranslateAndExecute(commands: List[str]):
    funcs = []
    for command in commands:
        if command.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))
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
            # "google search pratham pednekar", 
            # "open future of ai" 
            # "play AI revolution on YouTube", 
            # "open notepad", 
            # "open spotify", 
            #"content AI impact on jobs", 
            # "system mute"
        ]))
