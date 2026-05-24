export interface Message {
  id: string;
  messages: {
    senderId: string;
    receiverId: string;
    content: string;
    type: 'message' | 'message_call' | 'message_location';
    attachments?: { type: string; url: string; fileName: string }[];
    reacts: { like: boolean; love: boolean; haha: boolean; wow: boolean; sad: boolean };
    timestamp: string;
    readStatus: boolean;
    isDeleted: boolean;
  }[];
}