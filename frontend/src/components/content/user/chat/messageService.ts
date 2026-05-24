import axios from "axios";
import type { Message } from "./useChat";

const api = axios.create({ baseURL: "http://localhost:8000" });

api.interceptors.request.use((cfg) => {
  const t = localStorage.getItem("token");
  if (t) cfg.headers.Authorization = `Bearer ${t}`;
  return cfg;
});

type SendMessagePayload = {
  content: string;
  file?: string[];
  media?: string[];
};

export const messageAPI = {
  // ✅ FIX: match backend SendMessageRequest
  send: (
    receiver_email: string,
    payload: SendMessagePayload
  ) =>
    api.post<Message>("/message/send", {
      receiver_email,
      content: payload.content,
      file: payload.file ?? [],
      media: payload.media ?? [],
    }),

  getConversation: (
    other_email: string,
    skip = 0,
    limit = 50
  ) =>
    api.get<Message[]>(
      `/message/conversation/${other_email}?skip=${skip}&limit=${limit}`
    ),

  markRead: (other_email: string) =>
    api.post("/message/mark-read", { other_email }),
};