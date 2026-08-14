// src/hooks/useWebSocket.ts
import { useEffect, useRef } from "react";
import wsClient from "../lib/websocket";

/**
 * Mounts the WebSocket connection once on app mount.
 * Guards against HMR creating duplicate connections.
 */
export const useWebSocket = () => {
  const connected = useRef(false);

  useEffect(() => {
    if (connected.current) return; // HMR guard
    connected.current = true;
    wsClient.connect();

    return () => {
      // Only disconnect on real unmount (not HMR)
      connected.current = false;
      wsClient.disconnect();
    };
  }, []);
};

export default useWebSocket;
