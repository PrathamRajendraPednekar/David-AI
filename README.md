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

![Thor Image]([Generated_Images/thor.png](https://github.com/PrathamRajendraPednekar/David-AI/blob/main/Generated_Images/image_of_Thor.jpg))

---

### 🏛️ AI Generated Image – Jharkhand Monuments
*Monument-based AI image generation*

![Jharkhand Monuments](Generated_Images/jharkhand_monuments.png)

---

### 🖥️ David AI – GUI Interface
*Main interface for interacting with David AI*

![David AI GUI](Frontend/Graphics/gui.png)

---

## 🏗️ Project Architecture

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
