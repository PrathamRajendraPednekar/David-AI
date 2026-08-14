import asyncio
import os
import requests
import urllib.parse
from dotenv import dotenv_values

OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "Generated_Images")


def open_images(file_path):
    try:
        print(f"🖼️ Opening image: {file_path}")
        os.startfile(file_path)
    except Exception as e:
        print(f"❌ Unable to open image: {e}")


async def generate_images(prompt: str):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"🎨 Generating image for: {prompt}")
    
    # URL encode the prompt
    encoded_prompt = urllib.parse.quote(prompt)
    api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&private=true"
    
    response = await asyncio.to_thread(requests.get, api_url, timeout=120)

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}")

    file_path = os.path.join(OUTPUT_FOLDER, f"{prompt.replace(' ', '_')}.png")
    with open(file_path, "wb") as f:
        f.write(response.content)
    print(f"✅ Image saved at: {file_path}")

    # Broadcast the image path to the frontend chat window
    try:
        from Backend.Server import emit_image
        emit_image(os.path.abspath(file_path))
    except Exception as emit_err:
        print(f"[ImageGeneration] Warning: could not emit image to frontend: {emit_err}")

    open_images(file_path)


def GenerateImages(prompt: str):
    try:
        asyncio.run(generate_images(prompt))
    except Exception as e:
        print(f"[ImageGeneration] ❌ Error: {e}")
        raise



if __name__ == "__main__":
    test_prompt = input("Enter prompt to generate an image: ")
    GenerateImages(test_prompt)

