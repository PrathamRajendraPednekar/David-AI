// src/components/TypingIndicator.tsx
// Phase 3 — Animated 3-dot typing indicator for "David is thinking..."
import React from "react";

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex items-end gap-2 px-2">
      <div
        className="flex items-end gap-1 rounded-2xl rounded-bl-none px-4 py-3"
        style={{
          background: "rgba(255,255,255,0.04)",
          border: "1px solid rgba(255,255,255,0.07)",
        }}
      >
        <div className="flex items-center gap-1">
          <span
            className="typing-dot block rounded-full"
            style={{ width: 5, height: 5, background: "#22d3ee" }}
          />
          <span
            className="typing-dot block rounded-full"
            style={{ width: 5, height: 5, background: "#22d3ee" }}
          />
          <span
            className="typing-dot block rounded-full"
            style={{ width: 5, height: 5, background: "#22d3ee" }}
          />
        </div>
      </div>
      <span
        style={{ fontSize: 11, color: "rgba(255,255,255,0.25)", marginBottom: 8 }}
      >
        David
      </span>
    </div>
  );
};

export default TypingIndicator;
