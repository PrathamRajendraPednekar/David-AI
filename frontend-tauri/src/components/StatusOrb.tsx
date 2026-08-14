// src/components/StatusOrb.tsx
// Phase 2 — Pure CSS/SVG Glowing Ring Orb (Siri/Cortana style, Zero WebGL)
import React from "react";
import { motion } from "framer-motion";
import { AssistantStatus } from "../lib/store";

// ── Color Schemes per Status ──────────────────────────────────────────────────
const STATUS_COLORS: Record<
  AssistantStatus,
  { stop1: string; stop2: string; stop3: string }
> = {
  idle: {
    stop1: "#22d3ee",
    stop2: "#a78bfa",
    stop3: "#22d3ee",
  },
  listening: {
    stop1: "#22d3ee",
    stop2: "#38bdf8",
    stop3: "#06b6d4",
  },
  thinking: {
    stop1: "#c084fc",
    stop2: "#a855f7",
    stop3: "#7e22ce",
  },
  speaking: {
    stop1: "#22d3ee",
    stop2: "#f43f5e",
    stop3: "#a855f7",
  },
};

// ── Layered High-Visibility Drop Shadow Glows ─────────────────────────────────
const GLOW_FILTERS: Record<AssistantStatus, string> = {
  idle:
    "drop-shadow(0 0 10px #22d3ee) drop-shadow(0 0 24px rgba(34,211,238,0.7)) drop-shadow(0 0 50px rgba(167,139,250,0.6)) drop-shadow(0 0 90px rgba(34,211,238,0.4))",
  listening:
    "drop-shadow(0 0 14px #22d3ee) drop-shadow(0 0 36px #22d3ee) drop-shadow(0 0 70px rgba(56,189,248,0.85)) drop-shadow(0 0 120px rgba(34,211,238,0.6))",
  thinking:
    "drop-shadow(0 0 12px #c084fc) drop-shadow(0 0 30px #a855f7) drop-shadow(0 0 65px rgba(126,34,206,0.85)) drop-shadow(0 0 100px rgba(168,85,247,0.5))",
  speaking:
    "drop-shadow(0 0 16px #22d3ee) drop-shadow(0 0 40px #f43f5e) drop-shadow(0 0 80px rgba(34,211,238,0.9)) drop-shadow(0 0 130px rgba(244,63,94,0.7))",
};

export const StatusOrb: React.FC<{
  status: AssistantStatus;
  size?: number;
  mini?: boolean;
}> = ({ status, size = 320, mini = false }) => {
  const colors = STATUS_COLORS[status];
  const glow = GLOW_FILTERS[status];

  // Dimensions
  const viewSize = mini ? 44 : 320;
  const center = viewSize / 2;
  const strokeWidth = mini ? 3.5 : 14;
  const radius = center - strokeWidth - (mini ? 2 : 12);

  const gradientId = `ring-grad-${mini ? "mini" : "full"}-${status}`;

  return (
    <div
      style={{
        width: size,
        height: size,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
      }}
    >
      {/* Background radial glow cushion behind ring */}
      {!mini && (
        <motion.div
          aria-hidden
          animate={{
            opacity: status === "listening" || status === "speaking" ? 0.9 : 0.6,
            scale: status === "listening" ? 1.1 : 1.0,
          }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
          style={{
            position: "absolute",
            width: size * 0.75,
            height: size * 0.75,
            borderRadius: "50%",
            background:
              status === "thinking"
                ? "radial-gradient(circle, rgba(168,85,247,0.18) 0%, rgba(126,34,206,0.04) 60%, transparent 70%)"
                : status === "speaking"
                ? "radial-gradient(circle, rgba(244,63,94,0.16) 0%, rgba(34,211,238,0.06) 60%, transparent 70%)"
                : "radial-gradient(circle, rgba(34,211,238,0.18) 0%, rgba(167,139,250,0.05) 60%, transparent 70%)",
            pointerEvents: "none",
          }}
        />
      )}

      {/* SVG Ring with Framer Motion Animation */}
      <motion.svg
        width={size}
        height={size}
        viewBox={`0 0 ${viewSize} ${viewSize}`}
        style={{
          overflow: "visible",
          filter: mini ? "drop-shadow(0 0 6px #22d3ee)" : glow,
          transition: "filter 0.5s ease-in-out",
        }}
        animate={
          mini
            ? { rotate: [0, 360] }
            : status === "idle"
            ? {
                rotate: [0, 360],
                scale: [1, 1.03, 1],
                opacity: [0.8, 0.95, 0.8],
              }
            : status === "listening"
            ? {
                rotate: [0, 360],
                scale: [1, 1.08, 1],
                opacity: [0.9, 1, 0.9],
              }
            : status === "thinking"
            ? {
                rotate: [0, -360],
                scale: [0.96, 1.04, 0.96],
                opacity: [0.75, 1, 0.8, 1, 0.75],
              }
            : {
                rotate: [0, 360],
                scale: [1, 1.12, 0.98, 1.1, 1],
                opacity: [0.85, 1, 0.9, 1, 0.85],
              }
        }
        transition={
          mini
            ? { repeat: Infinity, duration: 12, ease: "linear" }
            : status === "idle"
            ? {
                rotate: { repeat: Infinity, duration: 20, ease: "linear" },
                scale: { repeat: Infinity, duration: 4, ease: "easeInOut" },
                opacity: { repeat: Infinity, duration: 4, ease: "easeInOut" },
              }
            : status === "listening"
            ? {
                rotate: { repeat: Infinity, duration: 6, ease: "linear" },
                scale: { repeat: Infinity, duration: 1.2, ease: "easeInOut" },
                opacity: { repeat: Infinity, duration: 1.2, ease: "easeInOut" },
              }
            : status === "thinking"
            ? {
                rotate: { repeat: Infinity, duration: 3.5, ease: "linear" },
                scale: { repeat: Infinity, duration: 1.6, ease: "easeInOut" },
                opacity: { repeat: Infinity, duration: 0.8, ease: "easeInOut" },
              }
            : {
                rotate: { repeat: Infinity, duration: 4, ease: "linear" },
                scale: { repeat: Infinity, duration: 0.5, ease: "easeInOut" },
                opacity: { repeat: Infinity, duration: 0.5, ease: "easeInOut" },
              }
        }
      >
        <defs>
          <linearGradient
            id={gradientId}
            x1="0%"
            y1="0%"
            x2="100%"
            y2="100%"
          >
            <stop offset="0%" stopColor={colors.stop1} />
            <stop offset="50%" stopColor={colors.stop2} />
            <stop offset="100%" stopColor={colors.stop3} />
          </linearGradient>
        </defs>

        {/* Outer Glow Halo Ring */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={`url(#${gradientId})`}
          strokeWidth={strokeWidth * 1.5}
          opacity={0.35}
        />

        {/* Primary Crisp Luminous Ring */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={`url(#${gradientId})`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
      </motion.svg>
    </div>
  );
};

export default StatusOrb;
