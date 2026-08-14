// src/components/MicButton.tsx
// Phase 2/5 — Mic toggle with ripple press animation and icon swap
import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, MicOff } from "lucide-react";

interface MicButtonProps {
  active: boolean;
  onToggle: () => void;
  size?: number;
}

export const MicButton: React.FC<MicButtonProps> = ({
  active,
  onToggle,
  size = 64,
}) => {
  const [rippling, setRippling] = useState(false);

  const handlePress = () => {
    setRippling(true);
    setTimeout(() => setRippling(false), 500);
    onToggle();
  };

  return (
    <motion.button
      onClick={handlePress}
      whileTap={{ scale: 0.90 }}
      whileHover={{ scale: 1.07 }}
      className="relative flex items-center justify-center rounded-full cursor-pointer overflow-visible"
      style={{
        width: size,
        height: size,
        border: "none",
        background: active
          ? "rgba(34, 211, 238, 0.12)"
          : "rgba(239, 68, 68, 0.12)",
        outline: "none",
        boxShadow: active
          ? "0 0 24px rgba(34,211,238,0.30), inset 0 0 1px rgba(34,211,238,0.4)"
          : "0 0 16px rgba(239,68,68,0.20), inset 0 0 1px rgba(239,68,68,0.3)",
        transition: "background 0.25s ease, box-shadow 0.25s ease",
      }}
    >
      {/* Outer glow ring */}
      <motion.span
        className="absolute inset-0 rounded-full"
        animate={{
          boxShadow: active
            ? [
                "0 0 0 0px rgba(34,211,238,0.4)",
                "0 0 0 10px rgba(34,211,238,0)",
              ]
            : "0 0 0 0px rgba(0,0,0,0)",
        }}
        transition={{ repeat: active ? Infinity : 0, duration: 1.6 }}
      />

      {/* Ripple effect on press */}
      <AnimatePresence>
        {rippling && (
          <motion.span
            key="ripple"
            className="absolute rounded-full pointer-events-none"
            initial={{ scale: 0.5, opacity: 0.6 }}
            animate={{ scale: 2.8, opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            style={{
              width: size,
              height: size,
              background: active
                ? "rgba(34,211,238,0.25)"
                : "rgba(239,68,68,0.25)",
              borderRadius: "50%",
            }}
          />
        )}
      </AnimatePresence>

      {/* Icon swap */}
      <AnimatePresence mode="wait">
        {active ? (
          <motion.span
            key="mic"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.5, opacity: 0 }}
            transition={{ duration: 0.15 }}
          >
            <Mic size={size * 0.38} color="#22d3ee" />
          </motion.span>
        ) : (
          <motion.span
            key="mic-off"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.5, opacity: 0 }}
            transition={{ duration: 0.15 }}
          >
            <MicOff size={size * 0.38} color="#ef4444" />
          </motion.span>
        )}
      </AnimatePresence>
    </motion.button>
  );
};

export default MicButton;
