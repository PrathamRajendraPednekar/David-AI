// src/views/HomeView.tsx
// Phase 2 — Reactive Orb view: 3D orb, status label, mic button, ambient background
import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAppState, AssistantStatus } from "../lib/store";
import { StatusOrb } from "../components/StatusOrb";
import { MicButton } from "../components/MicButton";
import wsClient from "../lib/websocket";

const STATUS_LABELS: Record<AssistantStatus, string> = {
  idle: "Available ...",
  listening: "Listening ...",
  thinking: "Thinking ...",
  speaking: "Speaking ...",
};

const STATUS_COLORS: Record<AssistantStatus, string> = {
  idle: "rgba(255,255,255,0.35)",
  listening: "#22d3ee",
  thinking: "#a855f7",
  speaking: "#22d3ee",
};

export const HomeView: React.FC = () => {
  const { status, micEnabled, setMicEnabled } = useAppState();

  const handleMicToggle = () => {
    const next = !micEnabled;
    setMicEnabled(next);
    wsClient.send("mic", { active: next });
  };

  return (
    <div
      className="flex flex-col items-center justify-center h-full ambient-bg relative overflow-hidden"
    >
      {/* Ambient radial vignette behind orb (Phase 5) */}
      <div
        aria-hidden
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse 55% 55% at 50% 48%, rgba(34,211,238,0.06) 0%, rgba(168,85,247,0.03) 40%, transparent 70%)",
          pointerEvents: "none",
        }}
      />

      {/* ── Orb canvas ── */}
      <div style={{ position: "relative" }}>
        <StatusOrb status={status} size={320} />

        {/* Outer glow ring based on status */}
        <motion.div
          className="absolute inset-0 rounded-full pointer-events-none"
          animate={{
            boxShadow:
              status === "listening"
                ? "0 0 60px rgba(34,211,238,0.35), 0 0 120px rgba(34,211,238,0.15)"
                : status === "speaking"
                ? "0 0 60px rgba(34,211,238,0.30), 0 0 120px rgba(168,85,247,0.12)"
                : status === "thinking"
                ? "0 0 40px rgba(168,85,247,0.25), 0 0 80px rgba(168,85,247,0.08)"
                : "0 0 30px rgba(34,211,238,0.10), 0 0 60px rgba(34,211,238,0.04)",
          }}
          transition={{ duration: 0.6, ease: "easeInOut" }}
        />
      </div>

      {/* ── Status label with AnimatePresence fade ── */}
      <div
        className="mt-8 flex flex-col items-center gap-2"
        style={{ minHeight: 52 }}
      >
        <AnimatePresence mode="wait">
          <motion.p
            key={status}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.22 }}
            style={{
              fontSize: 14,
              fontWeight: 500,
              letterSpacing: "0.12em",
              color: STATUS_COLORS[status],
              textTransform: "uppercase",
              fontFamily: "monospace",
            }}
          >
            {STATUS_LABELS[status]}
          </motion.p>
        </AnimatePresence>

        <p
          style={{
            fontSize: 12,
            color: "rgba(255,255,255,0.22)",
            textAlign: "center",
            maxWidth: 320,
            lineHeight: 1.6,
          }}
        >
          {status === "idle"
            ? 'Say "Call Ayush", "Generate an image", or type in Chat'
            : status === "listening"
            ? "I'm listening — speak your command"
            : status === "thinking"
            ? "Processing your request..."
            : "David is responding..."}
        </p>
      </div>

      {/* ── Mic Button ── */}
      <div className="mt-10">
        <MicButton active={micEnabled} onToggle={handleMicToggle} size={68} />
      </div>

      {/* ── Dev state switcher (remove before shipping) ── */}
      {import.meta.env.DEV && (
        <div
          className="absolute bottom-4 left-1/2 flex gap-2"
          style={{ transform: "translateX(-50%)" }}
        >
          {(["idle", "listening", "thinking", "speaking"] as AssistantStatus[]).map(
            (s) => (
              <button
                key={s}
                onClick={() => useAppState.getState().setStatus(s)}
                style={{
                  fontSize: 10,
                  padding: "3px 8px",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 4,
                  background:
                    status === s ? "rgba(34,211,238,0.15)" : "transparent",
                  color:
                    status === s ? "#22d3ee" : "rgba(255,255,255,0.3)",
                  cursor: "pointer",
                }}
              >
                {s}
              </button>
            )
          )}
        </div>
      )}
    </div>
  );
};

export default HomeView;
