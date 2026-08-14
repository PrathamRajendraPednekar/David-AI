// src/components/TopBar.tsx
// Phase 1 — Custom frameless top bar with drag region, pill nav, and window controls
// BUG FIX: data-tauri-drag-region moved OFF the root header — it was intercepting
// all pointer-down events at the OS/webview level before JS click handlers fired,
// making window control buttons unresponsive. Now only the left wordmark and center
// nav carry the drag region; the right controls div is fully pointer-event free.
import React, { useCallback } from "react";
import { motion } from "framer-motion";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { invoke } from "@tauri-apps/api/core";
import {
  Home,
  MessageSquare,
  Minus,
  Square,
  X,
  Pin,
} from "lucide-react";
import { useAppState } from "../lib/store";

const appWindow = getCurrentWindow();

interface TopBarProps {
  activeTab: "home" | "chat";
  onTabChange: (tab: "home" | "chat") => void;
}

export const TopBar: React.FC<TopBarProps> = ({ activeTab, onTabChange }) => {
  const { alwaysOnTop, setAlwaysOnTop } = useAppState();

  const handleMinimize = useCallback(async () => {
    try { await appWindow.minimize(); } catch (e) { console.error("[TopBar] minimize:", e); }
  }, []);

  const handleMaximize = useCallback(async () => {
    try { await appWindow.toggleMaximize(); } catch (e) { console.error("[TopBar] maximize:", e); }
  }, []);

  const handleClose = useCallback(async () => {
    try { await appWindow.close(); } catch (e) { console.error("[TopBar] close:", e); }
  }, []);

  const handlePin = useCallback(async () => {
    try {
      const newState = await invoke<boolean>("toggle_always_on_top");
      setAlwaysOnTop(newState);
    } catch (err) {
      console.error("[TopBar] toggle_always_on_top error:", err);
    }
  }, [setAlwaysOnTop]);

  const tabs = [
    { id: "home" as const, label: "Home", Icon: Home },
    { id: "chat" as const, label: "Console", Icon: MessageSquare },
  ];

  return (
    // NOTE: NO data-tauri-drag-region on this root element.
    // Only child sub-regions that don't contain interactive controls get it.
    <header
      className="relative flex items-center justify-between px-4 select-none"
      style={{
        height: "48px",
        background: "#0a0a0a",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        boxShadow: "0 1px 0 rgba(34,211,238,0.04), 0 2px 12px rgba(0,0,0,0.5)",
        flexShrink: 0,
        zIndex: 50,
        cursor: "default",
      }}
    >
      {/* ── LEFT: Wordmark — drag region is safe here, no buttons ── */}
      <div
        data-tauri-drag-region
        className="flex items-center gap-2.5 min-w-[140px]"
        style={{ cursor: "grab" }}
      >
        {/* Animated status orb */}
        <div className="relative flex items-center justify-center w-5 h-5" style={{ pointerEvents: "none" }}>
          <span
            className="absolute inset-0 rounded-full"
            style={{
              background:
                "radial-gradient(circle, rgba(34,211,238,0.9) 0%, rgba(34,211,238,0) 70%)",
              animation: "ping 2.5s cubic-bezier(0,0,0.2,1) infinite",
              opacity: 0.4,
            }}
          />
          <span
            className="relative block w-2 h-2 rounded-full"
            style={{ background: "#22d3ee" }}
          />
        </div>

        <span
          style={{
            fontWeight: 700,
            fontSize: "13px",
            letterSpacing: "0.08em",
            color: "#f4f4f5",
          }}
        >
          DAVID AI
        </span>
      </div>

      {/* ── CENTER: Pill Nav — also safe as drag region (buttons have stopPropagation) ── */}
      <nav
        data-tauri-drag-region
        className="flex items-center gap-1 rounded-full px-1"
        style={{
          background: "rgba(255,255,255,0.04)",
          border: "1px solid rgba(255,255,255,0.06)",
          padding: "3px",
          cursor: "grab",
        }}
      >
        {tabs.map(({ id, label, Icon }) => {
          const isActive = activeTab === id;
          return (
            <button
              key={id}
              onClick={(e) => { e.stopPropagation(); onTabChange(id); }}
              className="relative flex items-center gap-1.5 px-4 rounded-full cursor-pointer z-10"
              style={{
                height: "30px",
                fontSize: "12px",
                fontWeight: isActive ? 600 : 400,
                color: isActive ? "#22d3ee" : "rgba(255,255,255,0.45)",
                border: "none",
                background: "transparent",
                transition: "color 0.2s ease",
              }}
            >
              {isActive && (
                <motion.span
                  layoutId="tab-pill"
                  className="absolute inset-0 rounded-full"
                  style={{
                    background: "rgba(34,211,238,0.10)",
                    border: "1px solid rgba(34,211,238,0.20)",
                  }}
                  transition={{ type: "spring", stiffness: 380, damping: 30 }}
                />
              )}
              <Icon size={13} />
              <span className="relative z-10">{label}</span>
            </button>
          );
        })}
      </nav>

      {/* ── RIGHT: Controls — NO drag region here, pointer events must reach buttons ── */}
      <div
        className="flex items-center gap-1 min-w-[140px] justify-end"
        style={{ cursor: "default" }}
      >
        {/* Pin button */}
        <WinBtn
          onClick={handlePin}
          title={alwaysOnTop ? "Unpin window" : "Pin always on top"}
          hoverColor="#22d3ee"
          isActive={alwaysOnTop}
        >
          <Pin
            size={13}
            style={{ transform: alwaysOnTop ? "rotate(45deg)" : "none", transition: "transform 0.2s" }}
          />
        </WinBtn>

        <div style={{ width: 1, height: 16, background: "rgba(255,255,255,0.06)", margin: "0 2px" }} />

        <WinBtn onClick={handleMinimize} title="Minimize" hoverColor="#71717a">
          <Minus size={13} />
        </WinBtn>

        <WinBtn onClick={handleMaximize} title="Maximize / Restore" hoverColor="#71717a">
          <Square size={11} />
        </WinBtn>

        <WinBtn onClick={handleClose} title="Close" hoverColor="#ef4444" hoverBg="rgba(239,68,68,0.12)">
          <X size={14} />
        </WinBtn>
      </div>
    </header>
  );
};

// ── Reusable window control button ──────────────────────
const WinBtn: React.FC<{
  onClick: () => void;
  title: string;
  hoverColor?: string;
  hoverBg?: string;
  isActive?: boolean;
  children: React.ReactNode;
}> = ({ onClick, title, hoverColor = "#f4f4f5", hoverBg, isActive, children }) => (
  <motion.button
    title={title}
    onClick={(e) => { e.stopPropagation(); onClick(); }}
    whileHover={{ scale: 1.08 }}
    whileTap={{ scale: 0.92 }}
    className="flex items-center justify-center rounded-md cursor-pointer"
    style={{
      width: 28,
      height: 28,
      border: "none",
      background: isActive ? "rgba(34,211,238,0.10)" : "transparent",
      color: isActive ? "#22d3ee" : "rgba(255,255,255,0.40)",
      transition: "background 0.15s ease, color 0.15s ease",
    }}
    onMouseEnter={(e) => {
      (e.currentTarget as HTMLButtonElement).style.color = hoverColor;
      (e.currentTarget as HTMLButtonElement).style.background =
        hoverBg || "rgba(255,255,255,0.06)";
    }}
    onMouseLeave={(e) => {
      (e.currentTarget as HTMLButtonElement).style.color = isActive
        ? "#22d3ee"
        : "rgba(255,255,255,0.40)";
      (e.currentTarget as HTMLButtonElement).style.background = isActive
        ? "rgba(34,211,238,0.10)"
        : "transparent";
    }}
  >
    {children}
  </motion.button>
);

export default TopBar;
