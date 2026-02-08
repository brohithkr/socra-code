import type { WsMessage } from "./types";

export function createRoomSocket(baseUrl: string, roomId: string, playerId: string, name: string) {
  const wsUrl = baseUrl.replace("http", "ws");
  const socket = new WebSocket(`${wsUrl}/ws/${roomId}?player_id=${playerId}&name=${encodeURIComponent(name)}`);
  const listeners: Array<(message: WsMessage) => void> = [];

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as WsMessage;
      listeners.forEach((listener) => listener(data));
    } catch (err) {
      console.error("WS parse error", err);
    }
  };

  return {
    socket,
    send: (message: WsMessage) => {
      socket.send(JSON.stringify(message));
    },
    onMessage: (handler: (message: WsMessage) => void) => {
      listeners.push(handler);
    },
  };
}
