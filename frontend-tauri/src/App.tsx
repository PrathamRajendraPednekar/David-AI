// src/App.tsx
// Phase 1/5 — Root shell: window container, TopBar, AnimatePresence view transitions
import React, { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { useAppState } from "./lib/store";
import { useWebSocket } from "./hooks/useWebSocket";
import { TopBar } from "./components/TopBar";
import { HomeView } from "./views/HomeView";
import { ChatView } from "./views/ChatView";

const appWindow = getCurrentWindow();

// Phase 5 — Page transition variants
const PAGE_VARIANTS = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit:    { opacity: 0, y: -8 },
};

const App: React.FC = () => {
  useWebSocket(); // Phase 4 — mount WebSocket lifecycle

  const { activeTab, setActiveTab } = useAppState();


  // Track window resize events (used by TopBar internally)
  useEffect(() => {
    let unlisten: (() => void) | null = null;
    appWindow.onResized(() => {/* TopBar handles its own icon state */}).then((fn) => { unlisten = fn; });
    return () => { unlisten?.(); };
  }, []);

  return (
    /*
      The outermost div uses glass + rounded corners.
      On Windows the Mica/Acrylic effect from Rust (lib.rs) renders behind this.
      Background must be semi-transparent to let the OS blur show through.
    */
    <div
      className="flex flex-col glass"
      style={{
        width: "100vw",
        height: "100vh",
        borderRadius: 12,
        border: "1px solid rgba(255,255,255,0.07)",
        overflow: "hidden",
        boxShadow: "0 25px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.04)",
      }}
    >
      {/* Phase 1 — Top bar */}
      <TopBar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Phase 2/3/5 — View switcher with AnimatePresence transitions */}
      <main
        className="flex-1 relative overflow-hidden"
        style={{ background: "transparent" }}
      >
        <AnimatePresence mode="wait">
          {activeTab === "home" ? (
            <motion.div
              key="home"
              variants={PAGE_VARIANTS}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.20, ease: "easeInOut" }}
              style={{ position: "absolute", inset: 0 }}
            >
              <HomeView />
            </motion.div>
          ) : (
            <motion.div
              key="chat"
              variants={PAGE_VARIANTS}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.20, ease: "easeInOut" }}
              style={{ position: "absolute", inset: 0 }}
            >
              <ChatView />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default App;
