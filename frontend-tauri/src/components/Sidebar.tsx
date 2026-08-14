// src/components/Sidebar.tsx
// Collapsible conversation history sidebar — with inline rename + delete on hover
import React, { useCallback, useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, MessageSquare, Clock, MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import { useAppState, type Conversation } from "../lib/store";
import wsClient from "../lib/websocket";

// ─────────────────────────────────────────────────────────────
// ConvoRow — isolated component so each row has its OWN ref
// for the context menu. This is critical: a shared menuRef in
// the parent only ever points to the LAST rendered menu node,
// so clicking Delete on any row immediately fires the outside-
// click handler (because the click isn't inside the last node),
// which wipes deleteConfirmId before it can render.
// ─────────────────────────────────────────────────────────────
interface ConvoRowProps {
  convo: Conversation;
  isActive: boolean;
  renamingId: string | null;
  renameValue: string;
  setRenameValue: (v: string) => void;
  renameInputRef: React.RefObject<HTMLInputElement | null>;
  onLoad: (id: string) => void;
  onStartRename: (id: string, title: string) => void;
  onCommitRename: (id: string, original: string) => void;
  onCancelRename: () => void;
  onDeleteConfirm: (id: string) => void;
  formatDate: (iso: string) => string;
}

const ConvoRow: React.FC<ConvoRowProps> = ({
  convo,
  isActive,
  renamingId,
  renameValue,
  setRenameValue,
  renameInputRef,
  onLoad,
  onStartRename,
  onCommitRename,
  onCancelRename,
  onDeleteConfirm,
  formatDate,
}) => {
  const [hovered, setHovered] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  // Each row has its OWN ref — fixes the shared-ref bug
  const menuRef = useRef<HTMLDivElement>(null);

  const isRenaming = renamingId === convo.id;

  // Close this row's menu on outside click
  useEffect(() => {
    if (!menuOpen) return;
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
        setDeleteConfirm(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [menuOpen]);

  return (
    <div
      style={{ position: "relative", marginBottom: 2 }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Row button */}
      <motion.button
        whileHover={{ x: isRenaming ? 0 : 2 }}
        onClick={() => !isRenaming && onLoad(convo.id)}
        style={{
          width: "100%",
          display: "block",
          textAlign: "left",
          padding: "9px 36px 9px 12px",
          borderRadius: 8,
          background: isActive
            ? "rgba(34, 211, 238, 0.10)"
            : hovered || menuOpen
            ? "rgba(255,255,255,0.04)"
            : "transparent",
          border: isActive
            ? "1px solid rgba(34, 211, 238, 0.15)"
            : "1px solid transparent",
          cursor: isRenaming ? "default" : "pointer",
          transition: "background 0.12s ease, border 0.12s ease",
        }}
      >
        {/* Title: inline rename input OR plain text */}
        {isRenaming ? (
          <input
            ref={renameInputRef}
            value={renameValue}
            onChange={(e) => setRenameValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") { e.preventDefault(); onCommitRename(convo.id, convo.title); }
              else if (e.key === "Escape") { onCancelRename(); }
              e.stopPropagation();
            }}
            onBlur={() => onCommitRename(convo.id, convo.title)}
            onClick={(e) => e.stopPropagation()}
            style={{
              width: "100%",
              background: "rgba(34,211,238,0.07)",
              border: "1px solid rgba(34,211,238,0.35)",
              borderRadius: 5,
              padding: "2px 6px",
              color: "#e2f8fc",
              fontSize: 12.5,
              fontWeight: 500,
              outline: "none",
              fontFamily: "inherit",
              lineHeight: 1.4,
            }}
          />
        ) : (
          <div
            style={{
              fontSize: 12.5,
              fontWeight: 500,
              color: isActive ? "#22d3ee" : "rgba(255,255,255,0.75)",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
              lineHeight: 1.4,
            }}
          >
            {convo.title || "Untitled conversation"}
          </div>
        )}

        {/* Date + message count */}
        {!isRenaming && (
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 3 }}>
            <span style={{ fontSize: 10, color: "rgba(255,255,255,0.28)" }}>
              {formatDate(convo.date)}
            </span>
            <span style={{ fontSize: 10, color: "rgba(255,255,255,0.18)" }}>·</span>
            <span style={{ fontSize: 10, color: "rgba(255,255,255,0.28)" }}>
              {convo.messageCount} msg{convo.messageCount !== 1 ? "s" : ""}
            </span>
          </div>
        )}
      </motion.button>

      {/* "..." button — visible on hover or when menu is open */}
      {!isRenaming && (hovered || menuOpen) && (
        <button
          title="More options"
          onClick={(e) => {
            e.stopPropagation();
            if (menuOpen) {
              setMenuOpen(false);
              setDeleteConfirm(false);
            } else {
              setMenuOpen(true);
            }
          }}
          style={{
            position: "absolute",
            right: 6,
            top: "50%",
            transform: "translateY(-50%)",
            width: 24,
            height: 24,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            borderRadius: 5,
            border: "none",
            background: menuOpen ? "rgba(34,211,238,0.12)" : "rgba(255,255,255,0.07)",
            color: menuOpen ? "#22d3ee" : "rgba(255,255,255,0.5)",
            cursor: "pointer",
            transition: "background 0.12s, color 0.12s",
            flexShrink: 0,
            zIndex: 5,
          }}
        >
          <MoreHorizontal size={13} />
        </button>
      )}

      {/* Context menu — each row's own isolated ref */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            ref={menuRef}
            initial={{ opacity: 0, scale: 0.92, y: -4 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.92, y: -4 }}
            transition={{ duration: 0.1 }}
            style={{
              position: "absolute",
              right: 6,
              top: "calc(100% - 4px)",
              zIndex: 100,
              background: "#1a1a1f",
              border: "1px solid rgba(255,255,255,0.10)",
              borderRadius: 8,
              padding: "4px",
              minWidth: 150,
              boxShadow: "0 8px 24px rgba(0,0,0,0.5)",
            }}
          >
            {/* Rename */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                setDeleteConfirm(false);
                setMenuOpen(false);
                onStartRename(convo.id, convo.title || "Untitled conversation");
              }}
              style={{
                width: "100%",
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "7px 10px",
                borderRadius: 5,
                border: "none",
                background: "transparent",
                color: "rgba(255,255,255,0.75)",
                fontSize: 12,
                cursor: "pointer",
                textAlign: "left",
                transition: "background 0.1s",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = "rgba(255,255,255,0.06)";
                (e.currentTarget as HTMLButtonElement).style.color = "#fff";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = "transparent";
                (e.currentTarget as HTMLButtonElement).style.color = "rgba(255,255,255,0.75)";
              }}
            >
              <Pencil size={12} style={{ opacity: 0.6 }} />
              Rename
            </button>

            {/* Divider */}
            <div style={{ height: 1, background: "rgba(255,255,255,0.06)", margin: "3px 6px" }} />

            {/* Delete — two-step confirm */}
            {deleteConfirm ? (
              <div style={{ padding: "4px 6px" }}>
                <div style={{
                  fontSize: 11,
                  color: "rgba(255,255,255,0.45)",
                  marginBottom: 5,
                  paddingLeft: 2,
                }}>
                  Delete this chat?
                </div>
                <div style={{ display: "flex", gap: 4 }}>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      console.log("[Delete] Confirmed for id:", convo.id);
                      setMenuOpen(false);
                      setDeleteConfirm(false);
                      onDeleteConfirm(convo.id);
                    }}
                    style={{
                      flex: 1,
                      padding: "5px 0",
                      borderRadius: 5,
                      border: "1px solid rgba(239,68,68,0.35)",
                      background: "rgba(239,68,68,0.12)",
                      color: "#f87171",
                      fontSize: 11,
                      fontWeight: 600,
                      cursor: "pointer",
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLButtonElement).style.background = "rgba(239,68,68,0.25)";
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLButtonElement).style.background = "rgba(239,68,68,0.12)";
                    }}
                  >
                    Delete
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); setDeleteConfirm(false); }}
                    style={{
                      flex: 1,
                      padding: "5px 0",
                      borderRadius: 5,
                      border: "1px solid rgba(255,255,255,0.08)",
                      background: "transparent",
                      color: "rgba(255,255,255,0.45)",
                      fontSize: 11,
                      cursor: "pointer",
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLButtonElement).style.background = "rgba(255,255,255,0.06)";
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLButtonElement).style.background = "transparent";
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              /* First-click: show confirm prompt */
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  console.log("[Delete] Showing confirm for id:", convo.id);
                  setDeleteConfirm(true);
                }}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "7px 10px",
                  borderRadius: 5,
                  border: "none",
                  background: "transparent",
                  color: "rgba(248,113,113,0.75)",
                  fontSize: 12,
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "background 0.1s, color 0.1s",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.background = "rgba(239,68,68,0.08)";
                  (e.currentTarget as HTMLButtonElement).style.color = "#f87171";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.background = "transparent";
                  (e.currentTarget as HTMLButtonElement).style.color = "rgba(248,113,113,0.75)";
                }}
              >
                <Trash2 size={12} style={{ opacity: 0.75 }} />
                Delete
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────
// Main Sidebar
// ─────────────────────────────────────────────────────────────
export const Sidebar: React.FC = () => {
  const { sidebarOpen, conversations, activeConversationId, clearChat } = useAppState();

  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const renameInputRef = useRef<HTMLInputElement>(null);

  // Auto-focus rename input when it appears
  useEffect(() => {
    if (renamingId && renameInputRef.current) {
      renameInputRef.current.focus();
      renameInputRef.current.select();
    }
  }, [renamingId]);

  const handleNewChat = useCallback(() => {
    wsClient.send("new_chat", {});
    clearChat();
  }, [clearChat]);

  const handleLoadConversation = useCallback((id: string) => {
    if (renamingId) return;
    wsClient.send("load_conversation", { id });
    useAppState.getState().clearChat();
    useAppState.getState().setActiveConversationId(id);
  }, [renamingId]);

  const startRename = useCallback((id: string, currentTitle: string) => {
    setRenamingId(id);
    setRenameValue(currentTitle);
  }, []);

  const commitRename = useCallback((id: string, originalTitle: string) => {
    const trimmed = renameValue.trim();
    const finalTitle = trimmed || originalTitle;
    if (finalTitle !== originalTitle) {
      useAppState.getState().setConversations(
        useAppState.getState().conversations.map((c) =>
          c.id === id ? { ...c, title: finalTitle } : c
        )
      );
      wsClient.send("rename_conversation", { id, title: finalTitle });
    }
    setRenamingId(null);
    setRenameValue("");
  }, [renameValue]);

  const cancelRename = useCallback(() => {
    setRenamingId(null);
    setRenameValue("");
  }, []);

  const handleDeleteConfirm = useCallback((id: string) => {
    const state = useAppState.getState();
    const wasActive = id === state.activeConversationId;
    const remaining = state.conversations.filter((c) => c.id !== id);

    console.log("[Delete] Removing conversation:", id, "| wasActive:", wasActive, "| remaining:", remaining.length);

    // Remove from store immediately
    state.setConversations(remaining);

    // If the deleted chat was the active one, switch context
    if (wasActive) {
      if (remaining.length > 0) {
        const next = remaining[0];
        wsClient.send("load_conversation", { id: next.id });
        state.clearChat();
        state.setActiveConversationId(next.id);
      } else {
        wsClient.send("new_chat", {});
        state.clearChat();
      }
    }

    // Tell backend to delete the file — sent AFTER store update to avoid
    // the backend's conversations_list broadcast re-adding the item
    // before the optimistic removal takes effect.
    wsClient.send("delete_conversation", { id });
  }, []);

  const formatDate = (iso: string) => {
    try {
      const d = new Date(iso);
      const now = new Date();
      const diffDays = Math.floor((now.getTime() - d.getTime()) / 86400000);
      if (diffDays === 0) return "Today";
      if (diffDays === 1) return "Yesterday";
      if (diffDays < 7) return `${diffDays} days ago`;
      return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
    } catch {
      return "";
    }
  };

  return (
    <AnimatePresence initial={false}>
      {sidebarOpen && (
        <motion.aside
          key="sidebar"
          initial={{ width: 0, opacity: 0 }}
          animate={{ width: 280, opacity: 1 }}
          exit={{ width: 0, opacity: 0 }}
          transition={{ duration: 0.22, ease: [0.4, 0, 0.2, 1] }}
          style={{
            flexShrink: 0,
            overflow: "hidden",
            background: "#0d0d0f",
            borderRight: "1px solid rgba(255,255,255,0.05)",
            display: "flex",
            flexDirection: "column",
            height: "100%",
          }}
        >
          <div
            style={{
              width: 280,
              height: "100%",
              display: "flex",
              flexDirection: "column",
              overflow: "hidden",
            }}
          >
            {/* ── New Chat Button ── */}
            <div style={{ padding: "16px 12px 12px" }}>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
                onClick={handleNewChat}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "10px 14px",
                  borderRadius: 10,
                  background: "rgba(34, 211, 238, 0.08)",
                  border: "1px solid rgba(34, 211, 238, 0.18)",
                  color: "#22d3ee",
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: "pointer",
                  letterSpacing: "0.02em",
                  transition: "background 0.15s ease",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.background = "rgba(34, 211, 238, 0.14)";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.background = "rgba(34, 211, 238, 0.08)";
                }}
              >
                <Plus size={15} />
                New chat
              </motion.button>
            </div>

            {/* ── Section Header ── */}
            <div style={{ padding: "4px 16px 8px", display: "flex", alignItems: "center", gap: 6 }}>
              <Clock size={11} style={{ color: "rgba(255,255,255,0.25)" }} />
              <span style={{
                fontSize: 10,
                fontWeight: 600,
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                color: "rgba(255,255,255,0.25)",
              }}>
                Recents
              </span>
            </div>

            {/* ── Conversation List ── */}
            <div className="chat-scroll" style={{ flex: 1, overflowY: "auto", padding: "0 8px 16px" }}>
              {conversations.length === 0 ? (
                <div style={{
                  padding: "24px 16px",
                  textAlign: "center",
                  color: "rgba(255,255,255,0.18)",
                  fontSize: 12,
                  lineHeight: 1.6,
                }}>
                  <MessageSquare size={24} style={{ marginBottom: 8, opacity: 0.3 }} />
                  <div>No past conversations yet.</div>
                  <div style={{ marginTop: 4, fontSize: 11 }}>Your history will appear here.</div>
                </div>
              ) : (
                conversations.map((convo) => (
                  <ConvoRow
                    key={convo.id}
                    convo={convo}
                    isActive={convo.id === activeConversationId}
                    renamingId={renamingId}
                    renameValue={renameValue}
                    setRenameValue={setRenameValue}
                    renameInputRef={renameInputRef}
                    onLoad={handleLoadConversation}
                    onStartRename={startRename}
                    onCommitRename={commitRename}
                    onCancelRename={cancelRename}
                    onDeleteConfirm={handleDeleteConfirm}
                    formatDate={formatDate}
                  />
                ))
              )}
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
};

export default Sidebar;
