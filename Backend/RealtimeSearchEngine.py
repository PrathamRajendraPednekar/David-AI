# Backend/RealtimeSearchEngine.py
import datetime
import os
import json
import requests
import re
from dotenv import dotenv_values

# ==============================
# Load Environment Variables
# ==============================
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
SERP_API_KEY = env_vars.get("SERP_API_KEY")

System = f"""You are "David AI", an autonomous voice-enabled personal assistant designed to execute real-world tasks, not just provide answers.

CORE BEHAVIOR:
- Act like an intelligent agent that completes tasks.
- Do NOT just suggest — plan and execute.
- Think internally, respond naturally.

TASK EXECUTION:
- Understand the user’s intent.
- Ask only if essential information is missing.
- Generate the required content (message, file, plan, etc.).
- Prepare the action for execution.

CALL EXECUTION:
- Understand when the user wants to make a call (voice or video).
- Identify the contact name clearly.
- Automatically decide the platform (default: WhatsApp).
- Open the application and navigate to the contact.
- Initiate the correct call type (voice or video).

EXECUTION RULE:
- For normal tasks (drafting messages, writing content): proceed without asking.
- For sensitive actions (sending messages, deleting data):
  → Show the final result and proceed unless the user objects.
  → Use a soft confirmation style instead of asking directly.
- For Calls: Do NOT ask "Should I call?". Instead, use a natural action statement like "Calling Ayush on WhatsApp..." before executing.

COMMUNICATION STYLE:
- Short, clear, natural.
- No step-by-step explanations.
- Sound like a real assistant.
- Keep it fast, smooth, and action-oriented.

AUTOMATION:
- You can open apps, type, save files, send messages, search contacts, and click call buttons.
- Briefly mention actions while performing them.

SECURITY:
- Never perform critical actions blindly.
- Give the user a moment to interrupt if needed.

KNOWN CONTACTS:
- My Number: +918623083659
- Ayush's Number: +919892207022

Use whatsapp app if it is possible, if not then use whatsapp web.
"""

# ==============================
# Load or Create Chat Log
# ==============================
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "Data")
os.makedirs(DATA_DIR, exist_ok=True)
CHATLOG_PATH = os.path.join(DATA_DIR, "ChatLog.json")

try:
    with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
        messages = json.load(f)
except:
    messages = []
    with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4)

# ==============================
# SerpApi Google Search
# ==============================
def SerpApiSearch(query, num_results=7):
    if not SERP_API_KEY:
        return "[Error] SerpApi key missing in .env file."

    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": SERP_API_KEY,
        "engine": "google",
        "num": num_results,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get("organic_results", [])
            if not results:
                return "No relevant results found."

            # Collect title + snippet
            snippets = []
            for r in results[:num_results]:
                title = r.get("title", "")
                snippet = r.get("snippet", "")
                if snippet:
                    snippets.append(f"{title}. {snippet}")

            return " ".join(snippets)
        else:
            return f"[SerpApi Error] {response.status_code}"
    except Exception as e:
        return f"[SerpApi Exception] {e}"

# ==============================
# Smart Summarizer (Better)
# ==============================
import re

def SummarizeText(raw_text, max_sentences=3):
    """
    Summarizes the given raw search text into a professional, short,
    grammatically correct response — without incomplete '...' phrases.
    """
    if not raw_text or "[Error]" in raw_text:
        return "Sorry, I couldn't retrieve accurate information right now."

    # --- Clean raw text ---
    raw_text = re.sub(r'\s+', ' ', raw_text).strip()
    raw_text = re.sub(r'\.{2,}', '.', raw_text)  # remove '...' or '.....'

    # --- Split into sentences ---
    sentences = re.split(r'(?<=[.!?]) +', raw_text)

    # --- Filter out incomplete or short fragments ---
    clean_sentences = [s for s in sentences if len(s.split()) > 4 and not s.strip().endswith("...")]

    # --- Build short summary ---
    summary_text = " ".join(clean_sentences[:max_sentences]).strip()

    # --- Ensure smooth ending ---
    if summary_text and summary_text[-1] not in ".!?":
        summary_text += "."

    # --- Apply assistant tone ---
    formatted_summary = (
        f"{summary_text}"
    )

    return formatted_summary



# ==============================
# AI Clients (Groq Priority & Gemini Fallback)
# ==============================
try:
    import groq
    GroqAPIKey = env_vars.get("GroqAPIKey")
    if GroqAPIKey:
        groq_client = groq.Groq(api_key=GroqAPIKey)
    else:
        groq_client = None
except Exception:
    groq_client = None

try:
    import google.genai as genai
    GeminiAPIKey = env_vars.get("GeminiAPIKey")
    gemini_client = genai.Client(api_key=GeminiAPIKey)
except Exception:
    gemini_client = None

def Information():
    now = datetime.datetime.now()
    return (
        f"Real-time Info:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d %B %Y')}\n"
        f"Time: {now.strftime('%H:%M:%S')}\n"
    )

# ==============================
# Realtime Search Engine
# ==============================
def RealtimeSearchEngine(prompt):
    question_words = ["who", "what", "where", "when", "why", "how", "weather", "news", "price", "latest", "stock"]
    is_question = any(word in prompt.lower() for word in question_words)
    search_data = SerpApiSearch(prompt) if is_question else ""
    
    system_instructions = System + "\n" + Information()
    if search_data:
        system_instructions += f"\nSearch Data context if relevant:\n{search_data}"

    # Priority 1: Groq API
    if groq_client:
        try:
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": prompt}
                ]
            )
            raw_text = completion.choices[0].message.content.replace("*", "").strip()
            if "formatted as a text document" in prompt:
                return raw_text
            else:
                return raw_text.replace("\n", " ")
        except Exception as groq_e:
            print(f"[Groq Error] {groq_e}")

    # Priority 2: Gemini Fallback
    if gemini_client:
        try:
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_instructions}\nUser Query: {prompt}"
            )
            raw_text = response.text.replace("*", "").strip()
            if "formatted as a text document" in prompt:
                return raw_text
            else:
                return raw_text.replace("\n", " ")
        except Exception as e:
             print(f"[Gemini Error] {e}")

    # Fallback Priority 3
    if search_data:
        return SummarizeText(search_data)
    else:
        return "I am doing well, sir! How can I help you today?"

# ==============================
# Main Execution
# ==============================
if __name__ == "__main__":
    while True:
        prompt = input("Ask me anything: ")
        print(RealtimeSearchEngine(prompt))






# import google.genai as genai
# from googlesearch import search
# from json import load, dump
# import datetime
# from dotenv import dotenv_values

# # ==============================
# # Load Environment Variables
# # ==============================
# env_vars = dotenv_values(".env")
# Username = env_vars.get("Username", "User")
# Assistantname = env_vars.get("Assistantname", "Assistant")
# GeminiAPIKey = env_vars.get("GeminiAPIKey")

# # ==============================
# # Initialize Gemini Client (auto-detect version)
# # ==============================
# try:
#     try:
#         # Newer versions (most stable)
#         client = genai.Client(api_key=GeminiAPIKey)
#     except Exception:
#         # Legacy fallback for older builds
#         client = genai.Client({"api_key": GeminiAPIKey})
#     print("[RealtimeSearchEngine] ✅ Gemini client initialized successfully.")
# except Exception as e:
#     print(f"[RealtimeSearchEngine] ❌ Gemini client initialization failed: {e}")
#     client = None


# # ==============================
# # System Prompt
# # ==============================
# System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
# *** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
# *** Just answer the question from the provided data in a professional way and the answer should be little short. ***"""

# # ==============================
# # Load or Create Chat Log
# # ==============================
# try:
#     with open(r"Data\ChatLog.json", "r") as f:
#         messages = load(f)
# except:
#     messages = []
#     with open(r"Data\ChatLog.json", "w") as f:
#         dump(messages, f)

# # ==============================
# # Google Search Function
# # ==============================
# def GoogleSearch(query):
#     results = list(search(query, advanced=True, num_results=5))
#     Answer = ""
#     for i in results:
#         Answer += f"{i.title}\n{i.description}\n"
#     return Answer.strip()

# # ==============================
# # Answer Cleanup
# # ==============================
# def AnswerModifier(Answer):
#     lines = Answer.split('\n')
#     non_empty_lines = [line for line in lines if line.strip()]
#     return '\n'.join(non_empty_lines)

# # ==============================
# # Real-Time Info
# # ==============================
# def Information():
#     now = datetime.datetime.now()
#     return (
#         f"Use This Real-time Information if needed:\n"
#         f"Day: {now.strftime('%A')}\n"
#         f"Date: {now.strftime('%d')}\n"
#         f"Month: {now.strftime('%B')}\n"
#         f"Year: {now.strftime('%Y')}\n"
#         f"Time: {now.strftime('%H:%M:%S')}\n"
#     )

# # ==============================
# # Chat Memory
# # ==============================
# SystemChatBot = [
#     {"role": "system", "content": System},
#     {"role": "user", "content": "Hi"},
#     {"role": "assistant", "content": "Hello, how can I help you?"}
# ]

# # ==============================
# # Realtime Search + Gemini Response
# # ==============================
# def RealtimeSearchEngine(prompt):
#     global SystemChatBot, messages

#     # Load chat history
#     with open(r"Data\ChatLog.json", "r") as f:
#         messages = load(f)
#     messages.append({"role": "user", "content": prompt})

#     # Add Google search data
#     search_data = GoogleSearch(prompt)
#     SystemChatBot.append({"role": "system", "content": search_data})

#     # ==============================
#     # Generate response using Gemini API
#     # ==============================
#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=(
#             f"{System}\n{Information()}\nSearch Data:\n{search_data}\n"
#             f"User Query: {prompt}\n"
#             "Provide the exact answer (name if applicable), a brief description about the person or topic, "
#             "and optionally ask a relevant follow-up question."
#         )
#     )

#     Answer = response.text.strip()
#     messages.append({"role": "assistant", "content": Answer})

#     # Save updated chat log
#     with open(r"Data\ChatLog.json", "w") as f:
#         dump(messages, f, indent=4)

#     SystemChatBot.pop()
#     return AnswerModifier(Answer)

# # ==============================
# # Main Execution
# # ==============================
# if __name__ == "__main__":
#     while True:
#         prompt = input("Enter your query: ")
#         print(RealtimeSearchEngine(prompt))
