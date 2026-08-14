// src/views/ChatView.tsx
// Phase 3 & Polish — Chat/Console view: sidebar, header bar, message thread, input bar
// BUG FIXES applied:
//   - Message duplication: addMessage("user") stays for instant UI feedback.
//     Backend no longer echoes user messages (fixed in GUI.py ShowTextToScreen).
//   - Layout: sidebar + chat in a single horizontal flex row.
import React, { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Paperclip, Terminal, X as XIcon } from "lucide-react";
import { useAppState } from "../lib/store";
import { StatusOrb } from "../components/StatusOrb";
import { MicButton } from "../components/MicButton";
import { TypingIndicator } from "../components/TypingIndicator";
import { Sidebar } from "../components/Sidebar";
import wsClient from "../lib/websocket";

export const ChatView: React.FC = () => {
  const { messages, isTyping, status, micEnabled, setMicEnabled, addMessage, connectionStatus, sidebarOpen, toggleSidebar } =
    useAppState();
  const [inputVal, setInputVal] = useState("");
  const [attachedFile, setAttachedFile] = useState<string | null>(null);       // display name
  const [attachedFileData, setAttachedFileData] = useState<string | null>(null); // base64 data
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Auto-resize textarea
  useEffect(() => {
    if (textAreaRef.current) {
      textAreaRef.current.style.height = "auto";
      textAreaRef.current.style.height = `${Math.min(
        textAreaRef.current.scrollHeight,
        96
      )}px`;
    }
  }, [inputVal]);

  const handleSend = useCallback(() => {
    const text = inputVal.trim();
    if (!text) return;

    addMessage("user", text);
    wsClient.send("user_query", {
      text,
      attachedFile: attachedFile ?? undefined,
      imageData: attachedFileData ?? undefined,
    });
    setInputVal("");
    setAttachedFile(null);
    setAttachedFileData(null);
  }, [inputVal, attachedFile, attachedFileData, addMessage]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleAttach = () => fileInputRef.current?.click();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAttachedFile(file.name);
      // Read the file as base64 so we can send actual image data over WebSocket.
      // Storing only file.name was the root cause — the backend has no access to
      // the local filesystem path the browser used, so it always got "file not found".
      const reader = new FileReader();
      reader.onload = (ev) => {
        const result = ev.target?.result as string;
        // result is "data:image/png;base64,XXXX..." — strip the prefix, send raw base64
        const base64 = result.split(",")[1] ?? result;
        setAttachedFileData(base64);
      };
      reader.readAsDataURL(file);
    }
    e.target.value = "";
  };

  const handleMicToggle = () => {
    const next = !micEnabled;
    setMicEnabled(next);
    wsClient.send("mic_toggle", { active: next });
  };

  return (
    // Outer wrapper: horizontal flex — sidebar on left, chat column on right
    <div
      style={{
        display: "flex",
        flexDirection: "row",
        height: "100%",
        overflow: "hidden",
      }}
    >
      {/* ── Sidebar ── */}
      <Sidebar />

      {/* ── Chat column ── */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          flex: 1,
          minWidth: 0,
          overflow: "hidden",
          position: "relative",
        }}
        className="ambient-bg"
      >
        {/* ── Persistent Header Bar with Mini Orb ── */}
        <div
          className="flex items-center justify-between px-6 py-2.5"
          style={{
            flexShrink: 0,
            background: "rgba(10, 10, 10, 0.6)",
            borderBottom: "1px solid rgba(255, 255, 255, 0.06)",
            backdropFilter: "blur(12px)",
            zIndex: 20,
          }}
        >
          <div className="flex items-center gap-2">
            {/* Terminal icon doubles as sidebar toggle */}
            <button
              onClick={toggleSidebar}
              title={sidebarOpen ? "Hide sidebar" : "Show sidebar"}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: 26,
                height: 26,
                borderRadius: 6,
                border: "none",
                background: sidebarOpen ? "rgba(34,211,238,0.10)" : "transparent",
                color: sidebarOpen ? "#22d3ee" : "rgba(34,211,238,0.65)",
                cursor: "pointer",
                transition: "background 0.15s ease, color 0.15s ease",
                flexShrink: 0,
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = "rgba(34,211,238,0.15)";
                (e.currentTarget as HTMLButtonElement).style.color = "#22d3ee";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = sidebarOpen ? "rgba(34,211,238,0.10)" : "transparent";
                (e.currentTarget as HTMLButtonElement).style.color = sidebarOpen ? "#22d3ee" : "rgba(34,211,238,0.65)";
              }}
            >
              <Terminal size={14} />
            </button>
            <span
              style={{
                fontSize: 11,
                fontWeight: 600,
                letterSpacing: "0.1em",
                color: "rgba(255, 255, 255, 0.5)",
                textTransform: "uppercase",
              }}
            >
              Console
            </span>
          </div>

          {/* Connection status — top-right */}
          <div className="flex items-center gap-2">
            <span
              style={{
                display: "inline-block",
                width: 5,
                height: 5,
                borderRadius: "50%",
                background:
                  connectionStatus === "connected"
                    ? "#22d3ee"
                    : connectionStatus === "reconnecting"
                    ? "#f59e0b"
                    : "rgba(255, 255, 255, 0.2)",
                flexShrink: 0,
              }}
            />
            <span
              style={{
                fontSize: 10,
                fontFamily: "monospace",
                color:
                  connectionStatus === "connected"
                    ? "rgba(34, 211, 238, 0.6)"
                    : connectionStatus === "reconnecting"
                    ? "#f59e0b"
                    : "rgba(255, 255, 255, 0.2)",
                letterSpacing: "0.06em",
              }}
            >
              {connectionStatus.toUpperCase()}
            </span>
          </div>
        </div>

        {/* ── Message list ── */}
        <div
          className="chat-scroll px-6 py-4"
          style={{
            flex: "1 1 0",
            minHeight: 0,
            overflowY: "auto",
            paddingBottom: "12px",
            display: "flex",
            flexDirection: "column",
            gap: "14px",
          }}
        >
          <AnimatePresence initial={false}>
            {messages.length === 0 && (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col items-center justify-center h-full"
                style={{ minHeight: 280 }}
              >
                <p style={{ color: "rgba(255, 255, 255, 0.18)", fontSize: 13 }}>
                  No messages yet — start a conversation
                </p>
              </motion.div>
            )}

            {messages.map((msg) => {
              const isUser = msg.sender === "user";
              return (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -6 }}
                  transition={{ duration: 0.22, ease: "easeOut" }}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: isUser ? "flex-end" : "flex-start",
                    gap: 4,
                  }}
                >
                  {/* Sender label */}
                  <span
                    style={{
                      fontSize: 9.5,
                      fontWeight: 600,
                      letterSpacing: "0.08em",
                      color: isUser
                        ? "rgba(255, 255, 255, 0.32)"
                        : "rgba(34, 211, 238, 0.65)",
                      textTransform: "uppercase",
                      paddingLeft: isUser ? 0 : 4,
                      paddingRight: isUser ? 4 : 0,
                    }}
                  >
                    {isUser ? "You" : "David"}
                  </span>

                  {/* Bubble */}
                  <div
                    style={{
                      maxWidth: "75%",
                      padding: msg.imagePath ? "8px" : "10px 14px",
                      borderRadius: isUser
                        ? "16px 16px 4px 16px"
                        : "16px 16px 16px 4px",
                      background: isUser
                        ? "rgba(255, 255, 255, 0.06)"
                        : "rgba(34, 211, 238, 0.06)",
                      border: isUser
                        ? "1px solid rgba(255, 255, 255, 0.09)"
                        : "1px solid rgba(34, 211, 238, 0.22)",
                      boxShadow: isUser
                        ? "none"
                        : "0 0 14px rgba(34, 211, 238, 0.06)",
                      color: isUser ? "#f4f4f5" : "#e2f8fc",
                      fontSize: 13,
                      lineHeight: 1.65,
                      wordBreak: "break-word",
                      overflow: "hidden",
                    }}
                  >
                    {/* Text content */}
                    {msg.content && (
                      <div style={{ padding: msg.imagePath ? "4px 8px 8px" : undefined }}>
                        {msg.content}
                      </div>
                    )}

                    {/* Inline generated image */}
                    {msg.imagePath && (
                      <div
                        style={{
                          position: "relative",
                          borderRadius: 10,
                          overflow: "hidden",
                          cursor: "pointer",
                          marginTop: msg.content ? 6 : 0,
                        }}
                        title="Click to open full size"
                        onClick={() => window.open(msg.imagePath, "_blank")}
                      >
                        <img
                          src={msg.imagePath}
                          alt={msg.content}
                          style={{
                            display: "block",
                            width: "100%",
                            maxWidth: 340,
                            borderRadius: 10,
                            objectFit: "cover",
                          }}
                          onError={(e) => {
                            (e.currentTarget as HTMLImageElement).style.display = "none";
                          }}
                        />
                        {/* Hover overlay */}
                        <div
                          className="img-overlay"
                          style={{
                            position: "absolute",
                            inset: 0,
                            background: "rgba(0,0,0,0)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            transition: "background 0.2s ease",
                            borderRadius: 10,
                            fontSize: 11,
                            color: "rgba(255,255,255,0)",
                            letterSpacing: "0.06em",
                            fontWeight: 600,
                          }}
                          onMouseEnter={(e) => {
                            (e.currentTarget as HTMLDivElement).style.background = "rgba(0,0,0,0.35)";
                            (e.currentTarget as HTMLDivElement).style.color = "rgba(255,255,255,0.9)";
                          }}
                          onMouseLeave={(e) => {
                            (e.currentTarget as HTMLDivElement).style.background = "rgba(0,0,0,0)";
                            (e.currentTarget as HTMLDivElement).style.color = "rgba(255,255,255,0)";
                          }}
                        >
                          ↗ Open full size
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Timestamp */}
                  <span
                    style={{
                      fontSize: 9,
                      color: "rgba(255, 255, 255, 0.22)",
                      paddingLeft: isUser ? 0 : 4,
                      paddingRight: isUser ? 4 : 0,
                      fontFamily: "monospace",
                    }}
                  >
                    {msg.timestamp}
                  </span>
                </motion.div>
              );
            })}

            {/* Typing indicator */}
            {isTyping && (
              <motion.div
                key="typing"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
              >
                <TypingIndicator />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Scroll anchor */}
          <div ref={messagesEndRef} />
        </div>

        {/* ── Status strip (bottom) — mini orb + status label left, message count right ── */}
        <div
          className="px-6 py-1.5 flex items-center gap-2"
          style={{
            flexShrink: 0,
            borderTop: "1px solid rgba(255, 255, 255, 0.04)",
            fontSize: 10,
            fontFamily: "monospace",
            letterSpacing: "0.06em",
            background: "rgba(0, 0, 0, 0.3)",
          }}
        >
          {/* Mini orb + assistant status — bottom-left */}
          <StatusOrb status={status} size={32} mini />
          <span
            style={{
              color:
                status === "listening"
                  ? "#22d3ee"
                  : status === "thinking" || status === "speaking"
                  ? "#a855f7"
                  : "rgba(255, 255, 255, 0.3)",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
            }}
          >
            {status}
          </span>

          {/* Message count — bottom-right */}
          {messages.length > 0 && (
            <span style={{ marginLeft: "auto", color: "rgba(255,255,255,0.2)" }}>
              {messages.length} message{messages.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>

        {/* ── Input Bar ── */}
        <div
          className="flex items-end gap-2 px-4 py-3"
          style={{
            flexShrink: 0,
            background: "rgba(0, 0, 0, 0.5)",
            backdropFilter: "blur(16px)",
            borderTop: "1px solid rgba(255, 255, 255, 0.06)",
          }}
        >
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            style={{ display: "none" }}
            onChange={handleFileChange}
          />

          {/* Paperclip attach */}
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={handleAttach}
            title="Attach image for OCR/Vision"
            className="flex items-center justify-center rounded-full flex-shrink-0 cursor-pointer"
            style={{
              width: 38,
              height: 38,
              background: attachedFile
                ? "rgba(34, 211, 238, 0.12)"
                : "transparent",
              border: "1px solid rgba(255, 255, 255, 0.08)",
              color: attachedFile ? "#22d3ee" : "rgba(255, 255, 255, 0.35)",
              transition: "all 0.2s ease",
            }}
          >
            <Paperclip size={16} />
          </motion.button>

          {/* Text input pill */}
          <div
            className="flex-1 flex flex-col rounded-2xl px-4 py-2"
            style={{
              background: "rgba(255, 255, 255, 0.04)",
              border: "1px solid rgba(255, 255, 255, 0.08)",
              minHeight: 42,
              justifyContent: "flex-end",
            }}
          >
            {attachedFile && (
              <div
                className="flex items-center gap-1 mb-1.5"
                style={{ flexShrink: 0 }}
              >
                <div
                  className="flex items-center gap-1 px-2 py-0.5 rounded-full"
                  style={{
                    background: "rgba(34, 211, 238, 0.10)",
                    fontSize: 10,
                    color: "#22d3ee",
                    whiteSpace: "nowrap",
                    maxWidth: 160,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    border: "1px solid rgba(34,211,238,0.18)",
                  }}
                >
                  <Paperclip size={9} style={{ flexShrink: 0 }} />
                  <span style={{ overflow: "hidden", textOverflow: "ellipsis" }}>
                    {attachedFile}
                  </span>
                  {/* Remove attachment button */}
                  <button
                    onClick={(e) => { e.stopPropagation(); setAttachedFile(null); setAttachedFileData(null); }}
                    title="Remove attachment"
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      marginLeft: 2,
                      width: 13,
                      height: 13,
                      borderRadius: "50%",
                      border: "none",
                      background: "rgba(34,211,238,0.20)",
                      color: "#22d3ee",
                      cursor: "pointer",
                      flexShrink: 0,
                      padding: 0,
                      lineHeight: 1,
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLButtonElement).style.background = "rgba(239,68,68,0.35)";
                      (e.currentTarget as HTMLButtonElement).style.color = "#fca5a5";
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLButtonElement).style.background = "rgba(34,211,238,0.20)";
                      (e.currentTarget as HTMLButtonElement).style.color = "#22d3ee";
                    }}
                  >
                    <XIcon size={8} />
                  </button>
                </div>
              </div>
            )}
            <textarea
              ref={textAreaRef}
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message..."
              rows={1}
              style={{
                width: "100%",
                background: "transparent",
                border: "none",
                outline: "none",
                resize: "none",
                color: "#f4f4f5",
                fontSize: 13,
                lineHeight: 1.6,
                caretColor: "#22d3ee",
                fontFamily: "inherit",
                userSelect: "text",
                WebkitUserSelect: "text",
                maxHeight: 96,
                overflowY: "auto",
              }}
            />
          </div>

          {/* Mic toggle */}
          <MicButton active={micEnabled} onToggle={handleMicToggle} size={42} />

          {/* Send button */}
          <motion.button
            whileHover={inputVal.trim() ? { scale: 1.08 } : {}}
            whileTap={inputVal.trim() ? { scale: 0.92 } : {}}
            onClick={handleSend}
            disabled={!inputVal.trim()}
            className="flex items-center justify-center rounded-full flex-shrink-0 cursor-pointer"
            style={{
              width: 42,
              height: 42,
              background: inputVal.trim()
                ? "rgba(34, 211, 238, 0.15)"
                : "rgba(255, 255, 255, 0.03)",
              border: `1px solid ${
                inputVal.trim()
                  ? "rgba(34, 211, 238, 0.30)"
                  : "rgba(255, 255, 255, 0.06)"
              }`,
              color: inputVal.trim()
                ? "#22d3ee"
                : "rgba(255, 255, 255, 0.20)",
              transition: "all 0.2s ease",
            }}
          >
            {/* Paper plane icon */}
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </motion.button>
        </div>
      </div>
    </div>
  );
};

export default ChatView;
