import { create } from 'zustand';

interface ConnectionState {
  connected: boolean;
  reconnecting: boolean;
  reconnectAttempts: number;
  setConnected: (connected: boolean) => void;
  setReconnecting: (reconnecting: boolean) => void;
  setReconnectAttempts: (attempts: number) => void;
}

export const useConnectionStore = create<ConnectionState>((set) => ({
  connected: false,
  reconnecting: false,
  reconnectAttempts: 0,
  setConnected: (connected) => set({ connected }),
  setReconnecting: (reconnecting) => set({ reconnecting }),
  setReconnectAttempts: (reconnectAttempts) => set({ reconnectAttempts }),
}));
