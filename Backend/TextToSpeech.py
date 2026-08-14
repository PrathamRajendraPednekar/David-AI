import os
import asyncio
import edge_tts
import tempfile
import random
import warnings
import threading
import pygame
import time
from typing import Optional, Callable
from dotenv import dotenv_values

import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")

# =====================================================
# SETUP
# =====================================================
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

env_vars = dotenv_values(os.path.join(os.path.dirname(__file__), "..", ".env"))
AssistantVoice = env_vars.get("AssistantVoice", "en-US-ChristopherNeural")

TEMP_FILE = os.path.join(tempfile.gettempdir(), "assistant_tts.mp3")
_is_speaking = False  # Global flag

# =====================================================
# 1. Generate Speech File (Async)
# =====================================================
async def _generate_audio(text: str):
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch="+5Hz", rate="-10%")
    await communicate.save(TEMP_FILE)

# =====================================================
# 2. Play Speech (Non-blocking, with on_done callback)
# =====================================================
def _play_audio(on_done: Optional[Callable] = None):
    global _is_speaking
    try:
        _is_speaking = True
        pygame.mixer.init()
        pygame.mixer.music.load(TEMP_FILE)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy() and _is_speaking:
            pygame.time.Clock().tick(10)

        pygame.mixer.music.stop()
        pygame.mixer.quit()
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)
    except Exception as e:
        print(f"[TTS] Playback error: {e}")
    finally:
        _is_speaking = False
        # Fire on_done callback so caller can transition status (e.g. "Available ...")
        if on_done:
            try:
                on_done()
            except Exception as cb_err:
                print(f"[TTS] on_done callback error: {cb_err}")

# =====================================================
# 3. Public Functions
# =====================================================
def StopSpeech():
    """Immediately stop current speech playback."""
    global _is_speaking
    if _is_speaking:
        print("[STOP] Stopping speech playback...")
        _is_speaking = False
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except:
            pass

def TextToSpeech(text: str, on_done: Optional[Callable] = None):
    """Play text in a background thread, allowing interruption.
    
    Args:
        text: The text to speak.
        on_done: Optional callback fired when playback finishes (or errors).
                 Use this to transition assistant status back to idle.
    """
    global _is_speaking
    try:
        if _is_speaking:
            StopSpeech()  # stop any existing speech first

        # Trim overly long text
        parts = text.split(".")
        if len(parts) > 4 and len(text) > 250:
            responses = [
                "The rest of the result has been printed to the chat screen, kindly check it out sir.",
                "You can see the rest of the text on the chat screen, sir.",
                "Please check the chat screen for more information, sir.",
            ]
            text = ". ".join(parts[:2]) + ". " + random.choice(responses)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_generate_audio(text))

        threading.Thread(target=_play_audio, args=(on_done,), daemon=True).start()

    except Exception as e:
        print(f"[TTS] Error: {e}")
        _is_speaking = False
        # Still fire on_done so status resets even on failure
        if on_done:
            try:
                on_done()
            except Exception:
                pass

# =====================================================
# 4. Standalone Test
# =====================================================
if __name__ == "__main__":
    def _on_done():
        print("[TTS] Playback complete!")
    TextToSpeech("Testing if David can stop reading in between now.", on_done=_on_done)
    time.sleep(3)
    StopSpeech()
