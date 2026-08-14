// src/lib/store.ts
import { create } from "zustand";

export type AssistantStatus = "idle" | "listening" | "thinking" | "speaking";
export type ConnectionStatus = "connected" | "disconnected" | "reconnecting";

export interface Message {
  id: string;
  sender: "user" | "assistant";
  content: string;
  timestamp: string;
  imagePath?: string;  // local absolute path for generated images
}

export interface Conversation {
  id: string;         // filename without .json
  title: string;      // first user message or truncated summary
  date: string;       // ISO date string
  messageCount: number;
}

interface AppState {
  // Chat
  messages: Message[];
  isTyping: boolean;

  // Voice/assistant state
  status: AssistantStatus;
  micEnabled: boolean;

  // Window
  alwaysOnTop: boolean;
  activeTab: "home" | "chat";

  // WebSocket
  connectionStatus: ConnectionStatus;

  // Sidebar
  sidebarOpen: boolean;
  conversations: Conversation[];
  activeConversationId: string | null;

  // Actions
  addMessage: (sender: "user" | "assistant", content: string) => void;
  addImageMessage: (content: string, imagePath: string) => void;
  setStatus: (status: AssistantStatus) => void;
  setMicEnabled: (enabled: boolean) => void;
  setAlwaysOnTop: (enabled: boolean) => void;
  setActiveTab: (tab: "home" | "chat") => void;
  setConnectionStatus: (status: ConnectionStatus) => void;
  setIsTyping: (typing: boolean) => void;
  clearChat: () => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setConversations: (convos: Conversation[]) => void;
  setActiveConversationId: (id: string | null) => void;
}

export const useAppState = create<AppState>((set) => ({
  messages: [],
  isTyping: false,
  status: "idle",
  micEnabled: false,
  alwaysOnTop: false,
  activeTab: "home",
  connectionStatus: "disconnected",
  sidebarOpen: true,
  conversations: [],
  activeConversationId: null,

  addMessage: (sender, content) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: crypto.randomUUID(),
          sender,
          content,
          timestamp: new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ],
      isTyping: false,
    })),

  addImageMessage: (content, imagePath) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: crypto.randomUUID(),
          sender: "assistant" as const,
          content,
          imagePath,
          timestamp: new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ],
      isTyping: false,
    })),

  setStatus: (status) => set({ status }),
  setMicEnabled: (enabled) =>
    set({ micEnabled: enabled, status: enabled ? "listening" : "idle" }),
  setAlwaysOnTop: (enabled) => set({ alwaysOnTop: enabled }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  setConnectionStatus: (status) => set({ connectionStatus: status }),
  setIsTyping: (typing) => set({ isTyping: typing }),
  clearChat: () => set({ messages: [], isTyping: false, activeConversationId: null }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setConversations: (convos) => set({ conversations: convos }),
  setActiveConversationId: (id) => set({ activeConversationId: id }),
}));
