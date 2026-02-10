import vertexai
from vertexai.generative_models import GenerativeModel
from googlesearch import search
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve environment variables for the chatbot configuration.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

# Initialize Vertex AI and Gemini Pro model
vertexai.init(project="your-project-id", location="us-central1")
model = GenerativeModel("gemini-pro")

# Define the system instructions for the chatbot.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way.***"""

# Try to load the chat log from a JSON file, or create an empty one if it doesn't exist.
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)
    messages = []

# Function to perform a Google search and format the results.
def GoogleSearch(query):
    results = list(search(query, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"
    for url in results:
        Answer += f"{url}\n"
    Answer += "[end]"
    return Answer

# Function to clean up the answer by removing empty lines.
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# Predefined chatbot conversation system message and an initial user message.
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time information like the current date and time.
def Information():
    now = datetime.datetime.now()
    return (f"Use This Real-time Information if needed:\n"
            f"Day: {now.strftime('%A')}\n"
            f"Date: {now.strftime('%d')}\n"
            f"Month: {now.strftime('%B')}\n"
            f"Year: {now.strftime('%Y')}\n"
            f"Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds.\n")

# Function to handle the chat with real-time search and response generation.
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load the chat log
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)

    # Add user message
    messages.append({"role": "user", "content": prompt})

    # Add Google search results to system messages
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    # Generate response using Gemini Pro
    conversation = SystemChatBot + [{"role": "system", "content": Information()}] + messages
    response = model.predict(conversation, temperature=0.7, max_output_tokens=2048)
    Answer = response.text.strip()

    # Clean up the response
    messages.append({"role": "assistant", "content": Answer})

    # Save updated chat log
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    # Remove last system message from SystemChatBot
    SystemChatBot.pop()

    return AnswerModifier(Answer)

# Main interactive loop
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
