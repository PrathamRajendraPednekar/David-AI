import webbrowser
import time
import pyautogui
import asyncio
from typing import List

# Contact dictionary
CONTACTS = {
    "ayush mangela": "+919892207022",
    "mheet nmims": "+919969148543"
}

# Function to send WhatsApp message
def send_whatsapp_message(name, message):
    """Send a WhatsApp message instantly."""
    name = name.strip().lower()
    if name in CONTACTS:
        phone_number = CONTACTS[name]
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
        
        webbrowser.open(whatsapp_url)  # Open WhatsApp Web
        time.sleep(5)  # Wait for the page to load
        
        for _ in range(10):  # Try sending message
            pyautogui.press("enter")
            time.sleep(1)

        print(f"✅ Message sent to {name}: {message}")
    else:
        print(f"❌ Contact not found for: '{name}'")

# Async command executor
async def TranslateAndExecute(commands: List[str]):
    funcs = []
    for command in commands:
        if command.startswith("message "):
            rest = command.removeprefix("message ").strip().lower()

            # Match the contact name from CONTACTS
            for contact in CONTACTS.keys():
                if rest.startswith(contact):
                    name = contact
                    message = rest[len(contact):].strip()
                    funcs.append(asyncio.to_thread(send_whatsapp_message, name, message))
                    break
            else:
                print(f"❌ No contact match found in: '{rest}'")
        else:
            print(f"No Function Found for command: {command}")
    
    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

# Async automation runner
async def Automation(commands: List[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True

# Main runner
if __name__ == "__main__":
    asyncio.run(Automation([
        "message ayush mangela Hello, I am Jarvis!",
        # Add more commands here
    ]))
