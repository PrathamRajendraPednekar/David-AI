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

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Define user-agent for web requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize AI client
client = Groq(api_key=GroqAPIKey)

# List to store chatbot messages
messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'Chatbot')}, You're a content writer."}]


# ---- 1. GOOGLE SEARCH ----
def GoogleSearch(topic):
    """Search a topic on Google."""
    search(topic)
    return True


def search_google(query):
    """Perform a Google search and return HTML content."""
    url = f"https://www.google.com/search?q={query}"
    headers = {'User-Agent': USER_AGENT}
    response = requests.get(url, headers=headers)
    return response.text if response.status_code == 200 else None


# ---- 2. AI CONTENT GENERATION ----
def ContentWriterAI(prompt):
    """Generate AI-written content."""
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
    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content
    answer = answer.replace("</s>", "")
    messages.append({"role": "assistant", "content": answer})
    return answer


def Content(topic):
    """Generate content and save it to a file."""
    topic = topic.replace("Content ", "")
    content_by_ai = ContentWriterAI(topic)

    filepath = rf"Data\{topic.lower().replace(' ', '')}.txt"
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content_by_ai)

    OpenNotepad(filepath)
    return True


def OpenNotepad(file):
    """Open a text file in Notepad."""
    subprocess.run(["notepad.exe", file])


# ---- 3. YOUTUBE FUNCTIONS ----
def YouTubeSearch(topic):
    """Search for a topic on YouTube."""
    url = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(url)


def PlayYoutube(query):
    """Play a YouTube video based on query."""
    playonyt(query)
    return True


# ---- 4. APPLICATION CONTROL ----
def extract_links(html):
    """Extract links from Google search results."""
    if html is None:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True) if "url?q=" in a['href']]
    return links


def OpenApp(app):
    """Open an application or relevant webpage."""
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])
        return True


def CloseApp(app):
    """Close an application."""
    if "chrome" in app:
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False


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
System("mute")  # Mutes system volume
#System("volume up")  # Increases volume
#System("volume down")  # Decreases volume
#System("unmute")  # Unmutes system volume










