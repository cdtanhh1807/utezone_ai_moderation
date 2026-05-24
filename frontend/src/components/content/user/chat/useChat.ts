import { useEffect, useState } from "react";
import { messageAPI } from "./messageService";
import useWebSocket from "./useWebSocket";
import { useAuth } from "./AuthContext";

export type Message = {
  id?: string;
  sender_email: string;
  receiver_email: string;
  content: string;
  file?: string[];
  media?: string[];
  created_at: string;
  mine: boolean;
};

export default function useChat(otherEmail: string) {
  const { email } = useAuth();
  const realtime = useWebSocket(localStorage.getItem("token") || "");
  const [history, setHistory] = useState<Message[]>([]);

  /* ---------- load history ---------- */
  useEffect(() => {
    (async () => {
      const { data } = await messageAPI.getConversation(otherEmail);

      setHistory(
        data.map((m: any) => ({
          ...m,
          id: m._id || m.id,
          file: m.file ?? [],
          media: m.media ?? [],
          mine: m.sender_email === email,
        }))
      );
    })();
  }, [otherEmail, email]);

  /* ---------- mark-read ---------- */
  useEffect(() => {
    if (otherEmail) {
      messageAPI.markRead(otherEmail);
    }
  }, [otherEmail]);

  /* ---------- realtime ---------- */
  useEffect(() => {
    if (!realtime.length) return;

    realtime.forEach((m: any) => {
      const isMatch =
        (m.sender_email === otherEmail && m.receiver_email === email) ||
        (m.sender_email === email && m.receiver_email === otherEmail);

      if (!isMatch) return;

      const id = m._id || m.id;

      setHistory((h) => {
        const exists = h.some((x) => x.id === id);
        if (exists) return h;

        return [
          ...h,
          {
            ...m,
            id,
            file: m.file ?? [],
            media: m.media ?? [],
            mine: m.sender_email === email,
          },
        ];
      });

      // auto mark read nếu là tin nhận
      if (m.sender_email === otherEmail) {
        messageAPI.markRead(otherEmail);
      }
    });
  }, [realtime, otherEmail, email]);

  /* ---------- SEND MESSAGE (UPDATED) ---------- */
  const sendMessage = async (
    content: string,
    file?: string[],
    media?: string[]
  ) => {
    if (!content.trim() && !file?.length && !media?.length) return;

    const tempMessage: Message = {
      id: `temp-${Date.now()}`,
      sender_email: email,
      receiver_email: otherEmail,
      content,
      file: file ?? [],
      media: media ?? [],
      created_at: new Date().toISOString(),
      mine: true,
    };

    setHistory((h) => [...h, tempMessage]);

    await messageAPI.send(otherEmail, {
      content,
      file,
      media,
    });
  };

  /* ---------- sort ---------- */
  const sorted = [...history].sort(
    (a, b) =>
      new Date(a.created_at).getTime() -
      new Date(b.created_at).getTime()
  );

  return {
    messages: sorted,
    sendMessage,
  };
}