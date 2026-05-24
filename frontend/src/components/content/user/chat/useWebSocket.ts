import { useEffect, useRef, useState } from 'react';

export default function useWebSocket(token: string) {
  const [messages, setMessages] = useState<any[]>([]); // ✅ đổi từ Message -> any
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!token) return;
    if (ws.current?.readyState === WebSocket.OPEN) ws.current.close();

    ws.current = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

    ws.current.onmessage = (e) => {
      const payload = JSON.parse(e.data);
      setMessages((prev) => [...prev, payload]);
    };

    return () => ws.current?.close();
  }, [token]);

  return messages;
}