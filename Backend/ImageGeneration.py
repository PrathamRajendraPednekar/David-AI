import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

# Function to open and display a single image based on a given prompt
# def open_images(prompt):
#     folder_path = r"Generated_Images"  # ✅ Changed folder to 'Generated_Images'
#     prompt = prompt.replace(" ", "_")
#     image_file = f"{prompt}.jpg"
#     image_path = os.path.join(folder_path, image_file)

#     try:
#         img = Image.open(image_path)
#         print(f"Opening image: {image_path}")
#         img.show()
#     except IOError:
#         print(f"Unable to open {image_path}")

def open_images(prompt):
    folder_path = r"Generated_Images"
    prompt = prompt.replace(" ", "_")
    image_file = f"{prompt}.jpg"
    image_path = os.path.join(folder_path, image_file)

    try:
        print(f"Opening image: {image_path}")
        os.startfile(image_path)  # ✅ Show image to user
    except Exception as e:
        print(f"❌ Unable to open image: {e}")

# Hugging Face API setup
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Async function to send image generation request
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

# Async function to generate one image
async def generate_images(prompt: str):
    payload = {
        "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed = {randint(0, 1000000)}",
    }
    image_bytes = await query(payload)

    output_folder = "Generated_Images"  # ✅ Output folder updated
    os.makedirs(output_folder, exist_ok=True)  # ✅ Create folder if not exists

    file_path = os.path.join(output_folder, f"{prompt.replace(' ', '_')}.jpg")
    with open(file_path, "wb") as f:
        f.write(image_bytes)

# Wrapper function
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# Main loop to monitor file
while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read()

        Prompt, Status = Data.split(",")

        if Status == "True":
            print("Generating Images...")
            GenerateImages(prompt=Prompt)

            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")

            break
        else:
            sleep(1)

    except:
        pass
