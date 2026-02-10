# 🤖 David AI – Intelligent Desktop Assistant

David AI is a **Python-based intelligent voice assistant** with a modern GUI, capable of **speech recognition, real-time search, automation, image generation, chatbot conversations, and multimedia control**.  
It is designed as a **modular, scalable desktop AI system**.

---

## 🚀 Key Highlights

- 🎤 Speech-to-Text & Text-to-Speech interaction  
- 🧠 Decision Making Model (DMM) for intent classification  
- 🔍 Real-time web search engine  
- 🤖 Conversational chatbot  
- 🖼️ AI image generation (Text → Image)  
- ⚙️ System & application automation  
- 🖥️ Interactive graphical user interface (GUI)  
- 📁 Clean Frontend–Backend architecture  

---

## 🖼️ Visual Showcase

### 🔥 AI Generated Image – Thor  
*Generated using David AI Image Generation module*

<p align="center">
  <img src="https://github.com/PrathamRajendraPednekar/David-AI/blob/main/Generated_Images/image_of_Thor.jpg"
       alt="Thor Image"
       width="600"/>
</p>

---

### 🏛️ AI Generated Image – Jharkhand Monuments  
*Monument-based AI image generation*

<p align="center">
  <img src="https://github.com/PrathamRajendraPednekar/David-AI/blob/main/Generated_Images/jharkhand_monuments_images.jpg"
       alt="Jharkhand Monuments"
       width="600"/>
</p>

---

### 🖥️ David AI – Graphical User Interface (GUI)

#### 🔹 GUI 1 – David AI Main Interface  
*Primary interface of David AI where users interact using voice and controls*

<p align="center">
  <img src="https://github.com/PrathamRajendraPednekar/David-AI/blob/main/copy/GUI_1.png"
       alt="David AI Main Interface"
       width="750"/>
</p>

---

#### 💬 GUI 2 – Live Chat & Interaction View  
*Real-time conversation between the user and David AI*

<p align="center">
  <img src="https://github.com/PrathamRajendraPednekar/David-AI/blob/main/copy/GUI_2.png"
       alt="David AI Chat Interaction"
       width="750"/>
</p>

---

# 🧠 How David AI Works

David AI is a voice-enabled intelligent assistant designed to understand user commands, make decisions, and perform multiple actions through a unified system.

---

## 🔄 Workflow

1. 🎤 The user speaks through the **microphone**
2. 🗣️ Speech is converted into text using the **SpeechRecognition** module
3. 🧠 The **Decision Making Model (DMM)** analyzes and classifies the user’s intent
4. ⚙️ Based on the detected intent, David AI performs one or more actions:
   - 🤖 Chatbot response  
   - 🔍 Real-time web search  
   - ⚙️ System or application automation  
   - 🖼️ AI image generation
5. 🔊 The generated response is converted back into voice using **Text-to-Speech (TTS)**
6. 🖥️ All interactions are displayed live on the **Graphical User Interface (GUI)**

---

## ⚙️ Supported Voice Commands

```text
open chrome
close notepad
play music on spotify
google search artificial intelligence
youtube play python tutorial
generate image of thor
voice call john
video call mom
message hello how are you
exit

```
🏗️ Project Architecture

```text
David-AI/
│
├── Backend/
│   ├── Model.py                 # Decision Making Model (DMM)
│   ├── Chatbot.py               # Chatbot logic
│   ├── Automation.py            # System automation
│   ├── RealtimeSearchEngine.py  # Live web search
│   ├── SpeechToText.py          # Speech recognition
│   ├── TextToSpeech.py          # Voice output
│   ├── ImageGeneration.py       # Image generation engine
│   └── Extract_text.py          # OCR / text extraction
│
├── Frontend/
│   ├── GUI.py                   # GUI interface
│   ├── Graphics/                # GUI images & icons
│   └── Files/                   # Runtime & temp files
│
├── Data/
│   └── ChatLog.json             # Chat history
│
├── Generated_Images/            # AI generated images
├── Report_Of_Project/
│   └── report.docx              # Project report
├── Main.py                      # Application entry point
├── .env                         # Environment variables
└── README.md

```

## 🛠️ Installation & Setup

###  Run It By Each Line

```bash
git clone https://github.com/your-username/David-AI.git
cd David-AI
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
Username=YourName
Assistantname=David
python Main.py

