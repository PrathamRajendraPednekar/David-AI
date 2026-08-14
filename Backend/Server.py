# Backend/Server.py
import asyncio
import json
import threading
import os
import datetime
import time
import glob
import websockets

CONNECTED_CLIENTS = set()

CURRENT_STATE = {
    "status": "Available ...",
    "mic": False
}

LOOP = None
ACTIVE_CONVERSATION_ID = None

def broadcast_sync(payload):
    """Safely schedule a JSON broadcast onto the asyncio event loop from any thread."""
    global LOOP
    if LOOP and LOOP.is_running():
        asyncio.run_coroutine_threadsafe(_broadcast(payload), LOOP)

async def _broadcast(payload):
    if not CONNECTED_CLIENTS:
        return
    message = json.dumps(payload)
    websockets_to_remove = set()
    for websocket in list(CONNECTED_CLIENTS):
        try:
            await websocket.send(message)
        except Exception:
            websockets_to_remove.add(websocket)
            
    for ws in websockets_to_remove:
        CONNECTED_CLIENTS.discard(ws)

def emit_status(status_str):
    CURRENT_STATE["status"] = status_str
    val = status_str.lower()
    if "listen" in val:
        norm = "listening"
    elif any(k in val for k in ["think", "process", "analyz", "writ", "generat", "initiat", "prepar", "open"]):
        norm = "thinking"
    elif "speak" in val or "say" in val:
        norm = "speaking"
    else:
        norm = "idle"
        
    broadcast_sync({
        "type": "status",
        "value": norm
    })

def emit_message(sender, text):
    broadcast_sync({
        "type": "message",
        "sender": sender,
        "text": text,
        "timestamp": datetime.datetime.now().strftime("%I:%M %p")
    })

def emit_mic(active_bool):
    CURRENT_STATE["mic"] = active_bool
    broadcast_sync({
        "type": "mic",
        "active": active_bool
    })

def emit_error(error_msg):
    broadcast_sync({
        "type": "error",
        "message": error_msg
    })

def emit_image(file_path: str):
    """Read the generated image file and broadcast it as a base64 data URL.
    The frontend uses this directly as an <img src=...> — no file system permissions needed."""
    try:
        import base64
        with open(file_path, "rb") as f:
            img_bytes = f.read()
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        data_url = f"data:image/png;base64,{b64}"
        broadcast_sync({
            "type": "image",
            "dataUrl": data_url,
            "path": file_path.replace("\\", "/")
        })
    except Exception as e:
        print(f"[Server] emit_image error: {e}")

# =====================================================
# CONVERSATION MANAGEMENT HELPERS
# =====================================================

def get_conversations_list():
    conv_dir = os.path.join(os.path.dirname(__file__), "..", "Data", "conversations")
    if not os.path.exists(conv_dir):
        os.makedirs(conv_dir, exist_ok=True)
    files = glob.glob(os.path.join(conv_dir, "*.json"))
    conversations = []
    for f_path in files:
        try:
            with open(f_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "id" in data:
                    conversations.append({
                        "id": data["id"],
                        "title": data.get("title", "Untitled Conversation"),
                        "date": data.get("date", ""),
                        "messageCount": len(data.get("messages", []))
                    })
        except Exception as e:
            print(f"[WebSocket] Error reading conversation file {f_path}: {e}")
    # Sort conversations by id (timestamp string) descending to show newest first
    conversations.sort(key=lambda x: x["id"], reverse=True)
    return conversations

def save_and_archive_current():
    global ACTIVE_CONVERSATION_ID
    chatlog_path = os.path.join(os.path.dirname(__file__), "..", "Data", "ChatLog.json")
    if not os.path.exists(chatlog_path):
        return
    try:
        with open(chatlog_path, "r", encoding="utf-8") as f:
            messages = json.load(f)
        if not messages:
            return

        # Determine title from the first user message
        title = "New Conversation"
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "").strip()
                words = content.split()
                if words:
                    title = " ".join(words[:5]) + ("..." if len(words) > 5 else "")
                break

        conv_dir = os.path.join(os.path.dirname(__file__), "..", "Data", "conversations")
        os.makedirs(conv_dir, exist_ok=True)

        if ACTIVE_CONVERSATION_ID:
            # Overwrite the existing archived conversation
            archive_path = os.path.join(conv_dir, f"{ACTIVE_CONVERSATION_ID}.json")
            # Keep original creation date and id, update messages/title
            if os.path.exists(archive_path):
                with open(archive_path, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                date_str = old_data.get("date", datetime.datetime.utcnow().isoformat() + "Z")
            else:
                date_str = datetime.datetime.utcnow().isoformat() + "Z"
            
            archive_data = {
                "id": ACTIVE_CONVERSATION_ID,
                "title": title,
                "date": date_str,
                "messages": messages
            }
        else:
            # Create a brand new archive file
            timestamp = str(int(time.time()))
            date_str = datetime.datetime.utcnow().isoformat() + "Z"
            archive_path = os.path.join(conv_dir, f"{timestamp}.json")
            archive_data = {
                "id": timestamp,
                "title": title,
                "date": date_str,
                "messages": messages
            }
            # Set this as the active conversation ID
            ACTIVE_CONVERSATION_ID = timestamp

        with open(archive_path, "w", encoding="utf-8") as f:
            json.dump(archive_data, f, indent=4)

    except Exception as e:
        print(f"[WebSocket] Error archiving current chat: {e}")

def clear_active_chat():
    global ACTIVE_CONVERSATION_ID
    chatlog_path = os.path.join(os.path.dirname(__file__), "..", "Data", "ChatLog.json")
    try:
        with open(chatlog_path, "w", encoding="utf-8") as f:
            json.dump([], f)
        ACTIVE_CONVERSATION_ID = None
    except Exception as e:
        print(f"[WebSocket] Error clearing active chat: {e}")

def load_archived_conversation(convo_id):
    global ACTIVE_CONVERSATION_ID
    conv_dir = os.path.join(os.path.dirname(__file__), "..", "Data", "conversations")
    archive_path = os.path.join(conv_dir, f"{convo_id}.json")
    if not os.path.exists(archive_path):
        return None
    try:
        with open(archive_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        chatlog_path = os.path.join(os.path.dirname(__file__), "..", "Data", "ChatLog.json")
        with open(chatlog_path, "w", encoding="utf-8") as f:
            json.dump(data.get("messages", []), f, indent=4)
        
        ACTIVE_CONVERSATION_ID = convo_id
        return data.get("messages", [])
    except Exception as e:
        print(f"[WebSocket] Error loading conversation {convo_id}: {e}")
        return None

# =====================================================
# WEBSOCKET HANDLER
# =====================================================

async def handler(websocket, *args):
    print(f"[WebSocket] Client connected from {websocket.remote_address}")
    CONNECTED_CLIENTS.add(websocket)
    
    # 1. Send current status, mic state, and conversations list on connect
    try:
        norm_status = CURRENT_STATE["status"].lower()
        if "listen" in norm_status:
            st = "listening"
        elif any(k in norm_status for k in ["think", "process", "analyz", "writ", "generat", "initiat", "prepar", "open"]):
            st = "thinking"
        elif "speak" in norm_status or "say" in norm_status:
            st = "speaking"
        else:
            st = "idle"
            
        await websocket.send(json.dumps({"type": "status", "value": st}))
        await websocket.send(json.dumps({"type": "mic", "active": CURRENT_STATE["mic"]}))
        await websocket.send(json.dumps({"type": "conversations_list", "conversations": get_conversations_list()}))
        
        # 2. Send recent ChatLog.json history (last 20 messages)
        chatlog_path = os.path.join(os.path.dirname(__file__), "..", "Data", "ChatLog.json")
        if os.path.exists(chatlog_path):
            try:
                with open(chatlog_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
                    recent = history[-20:] if len(history) > 20 else history
                    formatted_messages = []
                    for item in recent:
                        role = item.get("role", "assistant")
                        sender = "user" if role == "user" else "assistant"
                        text = item.get("content", "")
                        if text:
                            formatted_messages.append({"sender": sender, "text": text})
                    await websocket.send(json.dumps({"type": "history", "messages": formatted_messages}))
            except Exception as hist_err:
                print(f"[WebSocket] Error reading history: {hist_err}")
    except Exception as e:
        print(f"[WebSocket] Error sending initial state: {e}")

    # 3. Listen for incoming messages from Frontend
    try:
        async for message_str in websocket:
            try:
                data = json.loads(message_str)
                msg_type = data.get("type")
                
                if msg_type in ["user_query", "query"]:
                    text = data.get("text", "").strip()
                    attached_file = data.get("attachedFile")   # display name only
                    image_data_b64 = data.get("imageData")     # base64 image bytes

                    full_query = text

                    if image_data_b64 and attached_file:
                        # Decode base64 → save to a temp file the backend can actually open
                        try:
                            import base64 as _b64
                            img_bytes = _b64.b64decode(image_data_b64)
                            # Save into Data/ with a stable name based on original filename
                            safe_name = "".join(
                                c for c in attached_file if c.isalnum() or c in "._- "
                            ).rstrip() or "uploaded_image.png"
                            temp_dir = os.path.join(os.path.dirname(__file__), "..", "Data")
                            os.makedirs(temp_dir, exist_ok=True)
                            saved_path = os.path.join(temp_dir, safe_name)
                            with open(saved_path, "wb") as img_f:
                                img_f.write(img_bytes)
                            print(f"[WebSocket] Image saved to: {saved_path}")
                            # Use the absolute path so Main.py can open it regardless of cwd
                            full_query = f"[IMAGE:{os.path.abspath(saved_path)}] {text}"
                        except Exception as img_save_err:
                            print(f"[WebSocket] Failed to save image: {img_save_err}")
                            # Fall back: at least send the text so the user gets a response
                            full_query = text
                    elif attached_file and not image_data_b64:
                        # Legacy path: bare filename (will likely fail in Main.py but keep for compat)
                        full_query = f"[IMAGE:{attached_file}] {text}"

                    if full_query:
                        from Backend.Main import RunMainExecution
                        threading.Thread(target=RunMainExecution, args=(full_query,), daemon=True).start()

                elif msg_type in ["mic_toggle", "mic"]:
                    active = data.get("active", False)
                    from Frontend.GUI import SetMicrophoneStatus
                    SetMicrophoneStatus("True" if active else "False")
                    emit_mic(active)

                elif msg_type == "new_chat":
                    # Archive current conversation
                    save_and_archive_current()
                    # Clear current chat log
                    clear_active_chat()
                    # Send clear confirmation
                    await websocket.send(json.dumps({"type": "chat_cleared"}))
                    # Broadcast updated list to all clients
                    await _broadcast({"type": "conversations_list", "conversations": get_conversations_list()})

                elif msg_type == "rename_conversation":
                    convo_id = data.get("id")
                    new_title = data.get("title", "").strip()
                    if convo_id and new_title:
                        conv_dir = os.path.join(os.path.dirname(__file__), "..", "Data", "conversations")
                        archive_path = os.path.join(conv_dir, f"{convo_id}.json")
                        if os.path.exists(archive_path):
                            try:
                                with open(archive_path, "r", encoding="utf-8") as f:
                                    conv_data = json.load(f)
                                conv_data["title"] = new_title
                                with open(archive_path, "w", encoding="utf-8") as f:
                                    json.dump(conv_data, f, indent=4)
                                # Broadcast updated list so all clients reflect the new name
                                await _broadcast({"type": "conversations_list", "conversations": get_conversations_list()})
                            except Exception as rename_err:
                                print(f"[WebSocket] Error renaming conversation {convo_id}: {rename_err}")

                elif msg_type == "delete_conversation":
                    convo_id = data.get("id")
                    if convo_id:
                        conv_dir = os.path.join(os.path.dirname(__file__), "..", "Data", "conversations")
                        archive_path = os.path.join(conv_dir, f"{convo_id}.json")
                        try:
                            if os.path.exists(archive_path):
                                os.remove(archive_path)
                            # If the deleted conversation was the active one, clear ChatLog too
                            if ACTIVE_CONVERSATION_ID == convo_id:
                                clear_active_chat()
                                await websocket.send(json.dumps({"type": "chat_cleared"}))
                            # Broadcast updated list to all clients
                            await _broadcast({"type": "conversations_list", "conversations": get_conversations_list()})
                        except Exception as del_err:
                            print(f"[WebSocket] Error deleting conversation {convo_id}: {del_err}")

                elif msg_type == "load_conversation":
                    convo_id = data.get("id")
                    if convo_id:
                        # Save current active first before switching
                        save_and_archive_current()
                        # Load new messages
                        loaded_msgs = load_archived_conversation(convo_id)
                        if loaded_msgs is not None:
                            # Send history update back to the client
                            formatted_messages = []
                            for item in loaded_msgs:
                                role = item.get("role", "assistant")
                                sender = "user" if role == "user" else "assistant"
                                text = item.get("content", "")
                                if text:
                                    formatted_messages.append({"sender": sender, "text": text})
                            await websocket.send(json.dumps({"type": "history", "messages": formatted_messages}))
                            # Broadcast updated lists in case counts/titles changed
                            await _broadcast({"type": "conversations_list", "conversations": get_conversations_list()})

            except Exception as parse_err:
                print(f"[WebSocket] Message parse error: {parse_err}")

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONNECTED_CLIENTS.discard(websocket)
        print(f"[WebSocket] Client disconnected.")

async def run_server():
    print("[WebSocket Server] Listening on ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()

def start_server_in_loop():
    global LOOP
    LOOP = asyncio.new_event_loop()
    asyncio.set_event_loop(LOOP)
    LOOP.run_until_complete(run_server())

def StartWebSocketServer():
    server_thread = threading.Thread(target=start_server_in_loop, daemon=True)
    server_thread.start()
    return server_thread
