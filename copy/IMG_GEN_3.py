import requests
from PIL import Image
from io import BytesIO
from dotenv import get_key
import os

# Load API Key
API_KEY = get_key('.env', 'HuggingFaceAPIKey')

# API URL for Stable Diffusion XL
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {API_KEY}"}

def generate_image(prompt):
    payload = {"inputs": prompt}
    print("🎨 Generating image, please wait...")

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        filename = prompt.replace(" ", "_") + ".png"
        filepath = os.path.join("Generated_Images", filename)

        os.makedirs("Generated_Images", exist_ok=True)
        image.save(filepath)
        image.show()
        print(f"✅ Image saved and opened: {filepath}")
    else:
        print(f"❌ Failed to generate image: {response.status_code}")
        print(response.text)

# 🔹 Example usage
#generate_image("tony stark")
