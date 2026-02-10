from groq import Groq  # Importing the Groq library to use its API.
from json import load, dump  # Importing functions to read and write JSON files.
import datetime  # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values  # Importing dotenv_values to read environment variables from a .env file.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve specific environment variables for username, assistant name, and API key.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client using the provided API key.
client = Groq(api_key=GroqAPIKey)

# Define the chat log file path.
chat_log_path = r"Data\ChatLog.json"

# Function to get real-time date and time information.
def RealtimeInformation():
    now = datetime.datetime.now()
    return f"Day: {now.strftime('%A')}, Date: {now.strftime('%d %B %Y')}, Time: {now.strftime('%H:%M:%S')}"

# Function to modify the chatbot's response for better formatting.
def AnswerModifier(Answer):
    lines = Answer.split('\n')  # Split the response into lines.
    non_empty_lines = [line for line in lines if line.strip()]  # Remove empty lines.
    return '\n'.join(non_empty_lines)  # Join the cleaned lines back together.

# Function to load existing chat logs or create a new one.
def load_chat_log():
    try:
        with open(chat_log_path, "r") as f:
            return load(f)
    except (FileNotFoundError, ValueError):  # Handles missing or corrupted JSON files
        with open(chat_log_path, "w") as f:
            dump([], f)
        return []

# Function to save chat logs.
def save_chat_log(messages):
    with open(chat_log_path, "w") as f:
        dump(messages, f, indent=4)

# Main chatbot function to handle user queries.
def ChatBot(Query):
    """ This function sends the user's query to the chatbot and returns the AI's response. """
    messages = load_chat_log()
    
    # System message providing chatbot context.
    System = f"""
    Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time understanding.
    *** Do not tell time until I ask, do not talk too much, just answer the question. ***
    *** Reply in only English, even if the question is in Hindi, reply in English. ***
    *** Do not provide notes in the output, just answer the question and never mention your training data. ***
    """
    
    SystemChatBot = [
        {"role": "system", "content": System},
        {"role": "system", "content": RealtimeInformation()}
    ]
    
    messages.append({"role": "user", "content": Query})
    
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",  # Specify the AI model to use.
            messages=SystemChatBot + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True
        )
    
        Answer = ""  # Initialize an empty string to store the AI's response.
        for chunk in completion:
            content = getattr(chunk.choices[0].delta, "content", "")
            if content:  # Only concatenate if content is not None
                Answer += content
    
        Answer = Answer.replace("</s>", "")  # Clean up any unwanted tokens.
        messages.append({"role": "assistant", "content": Answer})
        save_chat_log(messages)  # Save updated chat log.
    
        return AnswerModifier(Answer)
    
    except Exception as e:
        print(f"Error: {e}")
        save_chat_log([])  # Reset chat log on error.
        return "An error occurred. Please try again."

# Main program entry point.
if __name__ == "__main__":
    while True:
        user_input = input("Enter the Question: ")  # Prompt the user for a question.
        print(ChatBot(user_input))  # Call the chatbot function and print its response.
