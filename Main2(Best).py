import os
import threading
import subprocess
import json
from time import sleep
from asyncio import run
from dotenv import dotenv_values

# GUI Imports
from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    GetMicrophoneStatus,
    GetAssistantStatus,
    AnswerModifier,
    QueryModifier
)

# Backend Imports
from Backend.Model import FirstLayerDMM
from Backend.Chatbot import ChatBot
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.TextToSpeech import TextToSpeech
from Backend.SpeechToText import SpeechRecognition

# Load environment variables
env = dotenv_values(".env")
Username = env.get("Username", "User")
Assistantname = env.get("Assistantname", "Assistant")
DefaultMessage = f"{Username} : Hello {Assistantname}, How are you?\n{Assistantname} : Welcome {Username}. I am doing well. How may I help you?"

Functions = ["open", "close", "youtube play", "system", "content", "google search", "youtube search","voice call","video call","spotify play",
             "generate image","message"]
imagegen_path = os.path.join("Frontend", "Files", "ImageGeneration.data")
chatlog_path = os.path.join("Data", "ChatLog.json")

subprocesses = []

# Initialization
def InitChatIfEmpty():
    if not os.path.exists(chatlog_path):
        os.makedirs(os.path.dirname(chatlog_path), exist_ok=True)
        with open(chatlog_path, "w", encoding="utf-8") as f:
            json.dump([], f)

    with open(chatlog_path, "r", encoding="utf-8") as f:
        if len(f.read().strip()) < 5:
            with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as db:
                db.write("")
            with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as rp:
                rp.write(DefaultMessage)

def SyncChatToGUI():
    with open(chatlog_path, "r", encoding="utf-8") as f:
        chatlog = json.load(f)

    content = ""
    for entry in chatlog:
        role = Username if entry["role"] == "user" else Assistantname
        content += f"{role} : {entry['content']}\n"

    formatted = AnswerModifier(content)
    with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as db:
        db.write(formatted)
    with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as rp:
        rp.write(formatted)

def Setup():
    print("Initializing...")
    SetMicrophoneStatus("False")
    SetAssistantStatus("Available ...")
    ShowTextToScreen("")
    InitChatIfEmpty()
    SyncChatToGUI()

# 🎤 Query Processing
def RunMainExecution():
    SetAssistantStatus("Listening ...")
    Query = SpeechRecognition()

    if not Query or Query.lower() == "none":
        print(" No valid speech detected.")
        return

    print(f"[🗣️] User said: {Query}")
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking ...")

    decisions = FirstLayerDMM(Query)
    # Remove duplicate decisions
    decisions = list(set(decisions))

    # ✅ Fallback override if DMM misclassifies command
    if decisions and all(d.startswith("general") for d in decisions):
        if Query.lower().startswith("message ") or Query.lower().startswith("voice call ") or Query.lower().startswith("video call "):
            print(" DMM fallback triggered. Using raw query as automation command.")
            decisions = [Query.lower()]


    print(f"DMM Output: {decisions}")

    merged_query = " and ".join([" ".join(d.split()[1:]) for d in decisions if not d.startswith("exit")])
    image_trigger = any("generate" in d for d in decisions)
    automation_trigger = any(d.startswith(tuple(Functions)) for d in decisions)

    #  Image generation
    if image_trigger:
        with open(imagegen_path, "w", encoding="utf-8") as f:
            f.write(f"{merged_query},True")
        try:
            subprocess.Popen(["python", os.path.join("Backend", "ImageGeneration.py")])
            print("[🖼️] Image generation triggered.")
        except Exception as e:
            print(f"[❌] Failed to launch image generation: {e}")

    #  Automation
    if automation_trigger:
        try:
            run(Automation(decisions))
            print("[⚙️] Automation done.")
        except Exception as e:
            print(f"[❌] Automation error: {e}")

    #  Response Processing
    for task in decisions:
        if "exit" in task:
            TextToSpeech("Okay, Bye!")
            ShowTextToScreen(f"{Assistantname} : Okay, Bye!")
            os._exit(0)

        elif task.startswith("realtime"):
            SetAssistantStatus("Searching ...")
            answer = RealtimeSearchEngine(QueryModifier(task.removeprefix("realtime").strip()))
            ShowTextToScreen(f"{Assistantname} : {answer}")
            SetAssistantStatus("Answering ...")
            TextToSpeech(answer)
            return

        elif task.startswith("general"):
            SetAssistantStatus("Thinking ...")
            answer = ChatBot(QueryModifier(task.removeprefix("general").strip()))
            ShowTextToScreen(f"{Assistantname} : {answer}")
            SetAssistantStatus("Answering ...")
            TextToSpeech(answer)
            return

def VoiceThread():
    while True:
        if GetMicrophoneStatus() == "True":
            RunMainExecution()
        elif GetAssistantStatus() != "Available ...":
            SetAssistantStatus("Available ...")
        sleep(1)

def StartGUI():
    GraphicalUserInterface()

#  MAIN ENTRY
if __name__ == "__main__":
    Setup()
    threading.Thread(target=VoiceThread, daemon=True).start()
    StartGUI()
