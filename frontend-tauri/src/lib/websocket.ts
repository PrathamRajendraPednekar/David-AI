// src/lib/websocket.ts
// Phase 4 — WebSocket client with exponential-backoff reconnect + conversation management
import { useAppState, type Conversation } from "./store";

const WS_URL = "ws://localhost:8765";
const MAX_BACKOFF_MS = 16000;
const BASE_BACKOFF_MS = 1000;

class WebSocketClient {
  private socket: WebSocket | null = null;
  private reconnectAttempt = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private explicitClose = false;

  public connect() {
    this.explicitClose = false;
    this._tryConnect();
  }

  private _tryConnect() {
    if (
      this.socket &&
      (this.socket.readyState === WebSocket.OPEN ||
        this.socket.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    const store = useAppState.getState();

    if (this.reconnectAttempt > 0) {
      store.setConnectionStatus("reconnecting");
    }

    console.log(
      `[WS] Attempting connection (attempt ${this.reconnectAttempt + 1}) → ${WS_URL}`
    );

    try {
      this.socket = new WebSocket(WS_URL);

      this.socket.onopen = () => {
        console.log("[WS] Connected ✓");
        this.reconnectAttempt = 0;
        useAppState.getState().setConnectionStatus("connected");
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this._handleMessage(data);
        } catch {
          console.warn("[WS] Non-JSON payload received:", event.data);
        }
      };

      this.socket.onclose = (e) => {
        console.log(`[WS] Closed (code ${e.code}).`);
        useAppState.getState().setConnectionStatus("disconnected");
        if (!this.explicitClose) this._scheduleReconnect();
      };

      this.socket.onerror = () => {
        // onerror fires before onclose, so just log — onclose handles reconnect
        console.warn("[WS] Connection error.");
      };
    } catch (err) {
      console.error("[WS] Failed to instantiate WebSocket:", err);
      useAppState.getState().setConnectionStatus("disconnected");
      this._scheduleReconnect();
    }
  }

  private _handleMessage(data: {
    type: string;
    value?: string;
    sender?: string;
    text?: string;
    message?: string;
    path?: string;
    dataUrl?: string;
    timestamp?: string;
    active?: boolean;
    messages?: Array<{ role?: string; sender?: string; content?: string; text?: string }>;
    conversations?: Conversation[];
  }) {
    const store = useAppState.getState();
    switch (data.type) {
      case "status":
        if (data.value) {
          // Map Python backend status strings to frontend state
          const val = data.value.toLowerCase();
          if (val.includes("listen")) store.setStatus("listening");
          else if (
            val.includes("think") || val.includes("process") ||
            val.includes("analyz") || val.includes("writ") ||
            val.includes("generat") || val.includes("initiat") ||
            val.includes("prepar") || val.includes("open")
          ) store.setStatus("thinking");
          else if (val.includes("speak") || val.includes("say")) store.setStatus("speaking");
          else store.setStatus("idle");
        }
        break;

      case "message":
        if (data.text) {
          store.addMessage((data.sender || "assistant") as "user" | "assistant", data.text);
        }
        break;

      case "mic":
        if (typeof data.active === "boolean") {
          store.setMicEnabled(data.active);
        }
        break;

      case "history":
        if (Array.isArray(data.messages)) {
          const currentMessages = useAppState.getState().messages;
          // Only populate from history on fresh app start (store is empty).
          // On reconnect/HMR the store already has messages — skip to avoid duplication.
          if (currentMessages.length === 0) {
            data.messages.forEach((m) => {
              const sender = m.sender || (m.role === "user" ? "user" : "assistant");
              const text = m.text || m.content;
              if (text) store.addMessage(sender as "user" | "assistant", text);
            });
          }
        }
        break;

      case "image":
        if (data.dataUrl) {
          // dataUrl is a base64-encoded data: URL — use directly as <img src>
          const fileName = (data.path || "").split("/").pop() || "image";
          const label = fileName.replace(/_/g, " ").replace(/\.png$/, "");
          store.addImageMessage(`Generated: ${label}`, data.dataUrl);
        }
        break;

      case "conversations_list":
        if (Array.isArray(data.conversations)) {
          store.setConversations(data.conversations);
        }
        break;

      case "chat_cleared":
        // Backend confirmed new chat was started — clear local state
        store.clearChat();
        break;

      case "error":
        if (data.message || data.text) {
          const errMsg = data.message || data.text;
          store.addMessage("assistant", `[SYSTEM ERROR] ${errMsg}`);
          store.setStatus("idle");
        }
        break;

      default:
        console.log("[WS] Unknown message type:", data.type);
    }
  }

  /** Send any payload to the Python backend */
  public send(type: string, payload: Record<string, unknown> = {}) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type, ...payload }));
    } else {
      console.warn("[WS] Cannot send — socket not open.");
    }
  }

  private _scheduleReconnect() {
    if (this.reconnectTimer) return;
    const delay = Math.min(
      BASE_BACKOFF_MS * 2 ** this.reconnectAttempt,
      MAX_BACKOFF_MS
    );
    console.log(`[WS] Reconnecting in ${delay}ms...`);
    this.reconnectAttempt += 1;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this._tryConnect();
    }, delay);
  }

  public disconnect() {
    this.explicitClose = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.socket?.close();
    this.socket = null;
  }
}

export const wsClient = new WebSocketClient();
export default wsClient;
