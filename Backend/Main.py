# Backend/Main.py
import sys, os
import codecs

# Force UTF-8 encoding for stdout/stderr to prevent CP1252/UnicodeEncodeError on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import threading
import json
from time import sleep
from dotenv import dotenv_values

# ============= PATH FIX =============
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ============= FRONTEND IMPORTS =============
from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    GetMicrophoneStatus,
    GetAssistantStatus,
    AnswerModifier
)

# ============= BACKEND IMPORTS =============
from Backend.SpeechToText import SpeechRecognition
from Backend.TextToSpeech import TextToSpeech, StopSpeech
from Backend.ImageGeneration import GenerateImages
from Backend.RealtimeSearchEngine import RealtimeSearchEngine

# ============= ENVIRONMENT CONFIG =============
env = dotenv_values(os.path.join(os.path.dirname(__file__), "..", ".env"))
Username = env.get("Username", "User")
Assistantname = env.get("Assistantname", "Assistant")

DefaultMessage = (
    f"{Username} : Hello {Assistantname}, how are you?\n"
    f"{Assistantname} : Welcome {Username}. I am doing well. How may I help you?"
)

# ============= PATHS =============
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "Data")
CHATLOG_PATH = os.path.join(DATA_DIR, "ChatLog.json")
os.makedirs(DATA_DIR, exist_ok=True)

# ============================================================
# INITIALIZATION
# ============================================================
def InitChatIfEmpty():
    if not os.path.exists(CHATLOG_PATH):
        with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
        if len(f.read().strip()) < 5:
            with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as db:
                db.write("")
            with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as rp:
                rp.write(DefaultMessage)

def Setup():
    print("[Main] Setting up assistant...")
    try:
        from Backend.Server import StartWebSocketServer
        StartWebSocketServer()
    except Exception as ws_e:
        print(f"[WebSocket Server Error] {ws_e}")
    SetMicrophoneStatus("False")
    SetAssistantStatus("Available ...")
    ShowTextToScreen("")
    InitChatIfEmpty()
    print("[Setup] Complete.")

# ============================================================
# MAIN EXECUTION
# ============================================================
def RunMainExecution(Prompt=None):
    SetAssistantStatus("Listening ..." if not Prompt else "Processing typed query...")
    Query = Prompt if Prompt else SpeechRecognition()

    if not Query or Query.lower() == "none":
        print("[WARN] No valid speech or query detected.")
        SetAssistantStatus("Available ...")
        return

    # 🔹 Stop speech command check
    if "stop reading" in Query.lower() or "stop speaking" in Query.lower():
        StopSpeech()
        SetAssistantStatus("Available ...")
        print("[STOP] Speech playback stopped by voice command.")
        return

    print(f"[USER] User said: {Query}")
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking ...")

    Query_lower = Query.lower()

    # =============================
    # HELPER — Log messages to file
    # =============================
    def LogToChat(role, content):
        try:
            if not os.path.exists(CHATLOG_PATH):
                with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
                    json.dump([], f)

            with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            data.append({"role": role, "content": content})

            with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[⚠️ ChatLog Error] {e}")

    # Log user query
    LogToChat("user", Query)

    # VISION / IMAGE ANALYSIS
    if Query.startswith("[IMAGE:"):
        import re
        match = re.search(r'\[IMAGE:(.*?)\]', Query)
        if match:
            image_path = match.group(1).strip()
            prompt = Query.replace(match.group(0), "").strip()
            if not prompt:
                prompt = "Please analyze this image and extract all visible text."

            # ── Step 1: Verify the file actually exists ──
            if not os.path.exists(image_path):
                err_msg = f"Image file not found at path: {image_path}. Make sure the file was uploaded correctly."
                print(f"[Vision] {err_msg}")
                # ShowTextToScreen broadcasts via WebSocket internally — no separate emit needed
                ShowTextToScreen(f"{Assistantname} : {err_msg}")
                LogToChat("assistant", err_msg)
                SetAssistantStatus("Speaking ...")
                TextToSpeech("I could not find the image file. Please try attaching it again.", on_done=lambda: SetAssistantStatus("Available ..."))
                return

            try:
                SetAssistantStatus("Analyzing Image ...")

                # ── Step 2: Run OCR with EasyOCR ──
                try:
                    import easyocr
                    reader = easyocr.Reader(['en'], gpu=False, verbose=False)
                    extracted_data = reader.readtext(image_path, detail=0)
                except Exception as ocr_err:
                    raise RuntimeError(f"OCR engine failed: {ocr_err}")

                answer = '\n'.join(extracted_data).strip() if extracted_data else "No legible text was found in this image."

                # ── Step 3: Save to Content AI/ and open Notepad ──
                try:
                    import subprocess
                    content_ai_dir = os.path.join(os.path.dirname(__file__), "..", "Content AI")
                    os.makedirs(content_ai_dir, exist_ok=True)
                    content_path = os.path.join(content_ai_dir, "extracted_text.txt")
                    with open(content_path, "w", encoding="utf-8") as f:
                        f.write(f"--- IMAGE VISION REPORT ---\nPrompt: {prompt}\nFile: {os.path.basename(image_path)}\n\n")
                        f.write(answer)
                    subprocess.Popen(["notepad.exe", content_path])
                except Exception as save_err:
                    print(f"[Vision] Could not save to Notepad: {save_err}")

                # ── Step 4: Show extracted text in chat AND speak summary ──
                # ShowTextToScreen handles both the legacy GUI file write AND
                # the WebSocket emit_message broadcast internally — don't call
                # emit_message separately or the message will appear twice.
                ShowTextToScreen(f"{Assistantname} : {answer}")
                LogToChat("assistant", answer)

                # Speak a short summary (don't read out a wall of text)
                if len(answer) > 120:
                    spoken = f"I extracted the text from the image and opened it in Notepad. Here's a preview: {answer[:100]}..."
                else:
                    spoken = f"I found the following text: {answer}" if answer != "No legible text was found in this image." else answer

                SetAssistantStatus("Speaking ...")
                TextToSpeech(spoken, on_done=lambda: SetAssistantStatus("Available ..."))

            except Exception as e:
                print(f"[ERROR] Vision processing error: {e}")
                err_response = f"Image analysis failed — {e}"
                ShowTextToScreen(f"{Assistantname} : {err_response}")
                LogToChat("assistant", err_response)
                try:
                    from Backend.Server import emit_error
                    emit_error(str(e))
                except Exception:
                    pass
                SetAssistantStatus("Speaking ...")
                TextToSpeech("I ran into a problem analyzing the image.", on_done=lambda: SetAssistantStatus("Available ..."))

            finally:
                # ── Step 5: Clean up the temp uploaded image from Data/ ──
                # Keep Content AI/extracted_text.txt (user-visible output), but
                # remove the raw uploaded file so Data/ doesn't accumulate.
                try:
                    if os.path.exists(image_path) and os.path.dirname(os.path.abspath(image_path)) == os.path.abspath(DATA_DIR):
                        os.remove(image_path)
                        print(f"[Vision] Cleaned up temp image: {image_path}")
                except Exception as cleanup_err:
                    print(f"[Vision] Temp file cleanup skipped: {cleanup_err}")

        return

    # IMAGE GENERATION
    if any(phrase in Query_lower for phrase in ["generate image", "create image", "generate an image", "create an image", "generate a image", "create a image"]):
        prompt = Query.lower().replace("generate an image of", "").replace("create an image of", "").replace("generate a image of", "").replace("create a image of", "").replace("generate image of", "").replace("create image of", "").replace("generate an image", "").replace("create an image", "").replace("generate a image", "").replace("create a image", "").replace("generate image", "").replace("create image", "").strip()
        if prompt.endswith('.'): prompt = prompt[:-1].strip()
        
        if not prompt:
            response = "Please describe what image I should generate."
            ShowTextToScreen(f"{Assistantname} : {response}")
            LogToChat("assistant", response)
            SetAssistantStatus("Speaking ...")
            TextToSpeech(response, on_done=lambda: SetAssistantStatus("Available ..."))
            return

        try:
            SetAssistantStatus("Generating Image ...")
            GenerateImages(prompt)
            response = f"I have generated the image for {prompt}."
            ShowTextToScreen(f"{Assistantname} : {response}")
            LogToChat("assistant", response)
            SetAssistantStatus("Speaking ...")
            TextToSpeech(response, on_done=lambda: SetAssistantStatus("Available ..."))
        except Exception as e:
            print(f"[ERROR] Image generation error: {e}")
            response = "Failed to generate the image."
            SetAssistantStatus("Speaking ...")
            TextToSpeech(response, on_done=lambda: SetAssistantStatus("Available ..."))
            LogToChat("assistant", response)
        return

    # CONTENT WRITING & NOTEPAD
    is_content_request = any(word in Query_lower for word in ["write", "create", "draft", "make", "generate", "leave application"])
    has_content_type = any(word in Query_lower for word in ["essay", "application", "appilcation", "routine", "email", "emil", "emial", "letter", "poem", "resume", "article", "diet", "exercise", "content"])
    
    if (is_content_request and has_content_type) or "leave application" in Query_lower:
        try:
            SetAssistantStatus("Writing Content ...")
            
            # Determine file name
            file_name = "generated_content.txt"
            for word in ["essay", "application", "appilcation", "routine", "email", "emil", "emial", "letter", "poem", "resume", "article", "diet", "exercise"]:
                if word in Query_lower:
                    if word in ["emil", "emial"]: word = "email"
                    if word == "appilcation": word = "application"
                    
                    file_name = f"{word}.txt"
                    if word == "application" and "leave" in Query_lower:
                        file_name = "leave_application.txt"
                    elif word == "routine" and "diet" in Query_lower:
                        file_name = "diet_routine.txt"
                    elif word == "routine" and "exercise" in Query_lower:
                        file_name = "exercise_routine.txt"
                    break
            
            # Ask the engine to provide a detailed response for writing tasks
            detailed_query = Query + " (Please write a very detailed and comprehensive response for this request, formatted as a text document). Do not include conversational filler, just the content."
            answer = RealtimeSearchEngine(detailed_query)
            
            # Create Content AI folder
            content_ai_dir = os.path.join(os.path.dirname(__file__), "..", "Content AI")
            os.makedirs(content_ai_dir, exist_ok=True)
            
            # Save to a text file
            content_path = os.path.join(content_ai_dir, file_name)
            with open(content_path, "w", encoding="utf-8") as f:
                f.write(answer)
                
            # Open with Notepad
            import subprocess
            subprocess.Popen(["notepad.exe", content_path])
            
            # Make sure we do NOT show the full text in chat
            response = f"I have generated the {file_name.replace('.txt', '').replace('_', ' ')} and opened it in Notepad."
            ShowTextToScreen(f"{Assistantname} : {response}")
            LogToChat("assistant", response)
            SetAssistantStatus("Speaking ...")
            TextToSpeech(response, on_done=lambda: SetAssistantStatus("Available ..."))
        except Exception as e:
            print(f"[ERROR] Content writing error: {e}")
            response = "Failed to write the content."
            SetAssistantStatus("Speaking ...")
            TextToSpeech(response, on_done=lambda: SetAssistantStatus("Available ..."))
            LogToChat("assistant", response)
            
        return

    # ==========================================
    # CALL AUTOMATION
    # ==========================================
    is_call_request = ("call" in Query_lower) and not any(w in Query_lower for w in ["what", "how", "who", "why", "send", "message"])
    
    if is_call_request:
        try:
            SetAssistantStatus("Initiating Call ...")
            
            # Let the AI generate native confirmation (e.g., "Calling Ayush on WhatsApp...")
            answer = RealtimeSearchEngine(Query)
            if "I am doing well" in answer: 
                contact_name = "Ayush" if "ayush" in Query_lower else "the contact"
                if "video" in Query_lower:
                    answer = f"Starting a video call with {contact_name} on WhatsApp..."
                else:
                    answer = f"Calling {contact_name} on WhatsApp..."
            
            ShowTextToScreen(f"{Assistantname} : {answer}")
            LogToChat("assistant", answer)
            SetAssistantStatus("Speaking ...")
            TextToSpeech(answer)
            
            number = "+919892207022" if "ayush" in Query_lower else "+918623083659" if any(w in Query_lower for w in ["me", "my number", "mom", "myself"]) else ""
            
            # Extract dynamically if LLM works
            try:
                from Backend.RealtimeSearchEngine import groq_client, gemini_client
                extraction_prompt = (
                    f"Extract ONLY the target phone number for this call query: '{Query}'. "
                    "Known contacts: Ayush (+919892207022), My Number/Mom (+918623083659). "
                    "Format: NUMBER only."
                )
                
                if groq_client and not number:
                    try:
                        completion = groq_client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": extraction_prompt}]
                        )
                        number = completion.choices[0].message.content.strip().replace(" ", "").replace("-", "")
                    except Exception:
                        pass
                
                if gemini_client and not number:
                    try:
                        extraction_res = gemini_client.models.generate_content(
                            model="gemini-2.5-flash", 
                            contents=extraction_prompt
                        )
                        number = extraction_res.text.strip().replace(" ", "").replace("-", "")
                    except Exception:
                        pass
            except:
                pass
                
            if len(number) >= 10:
                import threading
                def execute_call():
                    try:
                        import webbrowser
                        import pyautogui
                        import os
                        from time import sleep
                        
                        is_video = "video" in Query_lower
                        print(f"[Call] Initiating {'Video' if is_video else 'Voice'} call to {number}")
                        
                        # Open WhatsApp Desktop to the specific chat
                        webbrowser.open(f"whatsapp://send?phone={number}")
                        sleep(6) # Give the desktop app time to load and bring to foreground
                        
                        img_dir = os.path.join(os.path.dirname(__file__), "Whatsup_calling")
                        call_img = os.path.join(img_dir, "Call.png")
                        voice_img = os.path.join(img_dir, "Voice_call.png")
                        video_img = os.path.join(img_dir, "Video_call.png")
                        
                        try:
                            # 1. Look for the general Call button and click it
                            call_loc = pyautogui.locateCenterOnScreen(call_img, confidence=0.85)
                            if call_loc:
                                pyautogui.moveTo(call_loc.x, call_loc.y, duration=0.3)
                                pyautogui.click()
                                sleep(2.0) # Wait for dropdown animation to fully stabilize
                                
                                # 2. Look for the specific Voice or Video call button within the dropdown
                                target_img = video_img if is_video else voice_img
                                # Use higher confidence (0.9) to prevent it from mistaking the original button again!
                                target_loc = pyautogui.locateCenterOnScreen(target_img, confidence=0.9)
                                
                                if target_loc:
                                    print(f"[Call Match] Main: {call_loc} -> Target: {target_loc}")
                                    
                                    # Anti-loop check: ensure it isn't just clicking the exact same button twice!
                                    if abs(target_loc.y - call_loc.y) < 10 and abs(target_loc.x - call_loc.x) < 10:
                                        print("[Call Error] False positive! Matched the primary button instead of the dropdown item.")
                                    else:
                                        pyautogui.moveTo(target_loc.x, target_loc.y, duration=0.5)
                                        pyautogui.click()
                                        print("[Call] Successfully auto-clicked dropdown interface.")
                                else:
                                    print("[Call Error] Dropdown option not matched on screen. Maybe confidence is too strict or image is different.")
                            else:
                                print("[Call Error] Primary call button not visible.")
                        except Exception as img_e:
                            print(f"[Call Image Error] {img_e}")
                            
                    except Exception as call_e:
                        print(f"[Call Error] {call_e}")
                        
                threading.Thread(target=execute_call, daemon=True).start()
            else:
                raise Exception("Number not found")
                
        except Exception as e:
            print(f"[ERROR] Call automation error: {e}")
            response = "Failed to initiate the call process."
            ShowTextToScreen(f"{Assistantname} : {response}")
            LogToChat("assistant", response)
            SetAssistantStatus("Speaking ...")
            TextToSpeech(response, on_done=lambda: SetAssistantStatus("Available ..."))
            return
            
        SetAssistantStatus("Available ...")
        return

    # WHATSAPP AUTOMATION
    is_whatsapp_request = (("send" in Query_lower and "message" in Query_lower) or 
                           "whatsapp" in Query_lower) and not any(word in Query_lower for word in ["what is", "how to", "who is"])
                           
    if is_whatsapp_request:
        try:
            SetAssistantStatus("Preparing Message ...")
            
            # Let the AI generate the natural conversational response based on the new autonomous prompt
            answer = RealtimeSearchEngine(Query)
            if "I am doing well" in answer: # Gemini fallbacks due to limits
                answer = "Message ready. Sending it on WhatsApp now..."
            
            ShowTextToScreen(f"{Assistantname} : {answer}")
            LogToChat("assistant", answer)
            SetAssistantStatus("Speaking ...")
            TextToSpeech(answer)
            
            # Parse execution action (Groq with Gemini Fallback)
            from Backend.RealtimeSearchEngine import groq_client, gemini_client
            number = ""
            message_text = ""
            extracted_raw = ""
            
            try:
                extraction_prompt = (
                    f"Analyze this query: '{Query}'. Extract the target phone number and the intended message content. "
                    "Use these known contacts: Ayush (+919892207022), My Number (+918623083659). "
                    "If the user says 'my number' or 'me', use My Number. If 'Ayush', use his. "
                    "Format the response EXACTLY as: NUMBER|MESSAGE . Do not include any other labels or text."
                )
                
                if groq_client:
                    try:
                        completion = groq_client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": extraction_prompt}]
                        )
                        extracted_raw = completion.choices[0].message.content.strip()
                    except Exception:
                        pass
                
                if gemini_client and not extracted_raw:
                    try:
                        extraction_res = gemini_client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=extraction_prompt
                        )
                        extracted_raw = extraction_res.text.strip()
                    except Exception:
                        pass
                        
                if extracted_raw:
                    extracted_data = extracted_raw.split('|')
                    if len(extracted_data) >= 2:
                        number = extracted_data[0].strip()
                        message_text = extracted_data[1].strip()
            except Exception as e:
                print(f"[WhatsApp LLM Parse Error] {e}")
                pass
            
            # Hardcoded fallback if LLM quota is exhausted
            if not number or len(number) < 10:
                number = "+919892207022" if "ayush" in Query_lower else "+918623083659" if any(w in Query_lower for w in ["me", "my number", "myself"]) else ""
                message_text = Query.split("that")[-1].strip() if "that" in Query_lower else Query
                
            if len(number) >= 10:
                SetAssistantStatus("Opening WhatsApp ...")
                import threading
                
                def send_wa():
                    try:
                        import pywhatkit
                        print(f"[WhatsApp] Sending '{message_text}' to {number}")
                        # wait_time=15 gives the user 15 seconds to abort in the browser
                        pywhatkit.sendwhatmsg_instantly(number, message_text, wait_time=15, tab_close=True, close_time=3)
                    except Exception as wa_e:
                        print(f"[WhatsApp Error] {wa_e}")
                        
                threading.Thread(target=send_wa, daemon=True).start()
            else:
                raise Exception("Invalid number extracted or target unrecognized.")
        except Exception as e:
            print(f"[ERROR] WhatsApp automation error: {e}")
            response = "Failed to organize the WhatsApp routine due to API limits or missing number."
            ShowTextToScreen(f"{Assistantname} : {response}")
            LogToChat("assistant", response)
            SetAssistantStatus("Speaking ...")
            TextToSpeech(response, on_done=lambda: SetAssistantStatus("Available ..."))
            return
            
        SetAssistantStatus("Available ...")
        return

    # REALTIME SEARCH OR CHAT
    try:
        SetAssistantStatus("Thinking ...")
        answer = RealtimeSearchEngine(Query)
        ShowTextToScreen(f"{Assistantname} : {answer}")
        LogToChat("assistant", answer)
        SetAssistantStatus("Speaking ...")
        TextToSpeech(answer, on_done=lambda: SetAssistantStatus("Available ..."))
    except Exception as e:
        print(f"[ERROR] RealtimeSearchEngine error: {e}")
        response = "Sorry, I couldn't fetch the answer right now."
        ShowTextToScreen(f"{Assistantname} : {response}")
        try:
            from Backend.Server import emit_error
            emit_error(f"Backend Exception: {str(e)}")
        except Exception:
            pass
        LogToChat("assistant", response)
        SetAssistantStatus("Speaking ...")
        TextToSpeech(response, on_done=lambda: SetAssistantStatus("Available ..."))

    return


# ============================================================
# BACKGROUND THREAD
# ============================================================
def VoiceThread():
    print("[VoiceThread] Started")
    typed_path = TempDirectoryPath("TypedQuery.data")
    while True:
        try:
            if os.path.exists(typed_path):
                with open(typed_path, "r", encoding='utf-8') as f:
                    typed_text = f.read().strip()
                os.remove(typed_path)
                if typed_text:
                    RunMainExecution(typed_text)
                    continue

            if GetMicrophoneStatus() == "True":
                RunMainExecution()
            elif GetAssistantStatus() != "Available ...":
                SetAssistantStatus("Available ...")
        except Exception as e:
            print(f"[VoiceThread Error] {e}")
        sleep(0.5)

# ============================================================
# MAIN ENTRY POINT
# ============================================================
if __name__ == "__main__":
    print("[Main] Launching David AI Backend...")
    Setup()

    print("[Thread] Starting VoiceThread...")
    threading.Thread(target=VoiceThread, daemon=True).start()

    print("[WebSocket Server] David AI Backend ready on ws://localhost:8765")
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("[Main] Shutting down...")
