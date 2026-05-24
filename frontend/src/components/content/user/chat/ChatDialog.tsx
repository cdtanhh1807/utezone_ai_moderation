import "./ChatDialog.css";
import React, { useState, useRef } from "react";
import ConversationList from "./ConversationList";
import MessagePanel from "./MessagePanel";
import { messageAPI } from "./messageService";
import type { Conversation } from "./useConversation";

type Props = {
  onClose: () => void;
  list: Conversation[];
  refetch: () => void;
};

const ChatDialog: React.FC<Props> = ({ onClose, list, refetch }) => {
  const dialogRef = useRef<HTMLDivElement>(null);
  const [selected, setSelected] = useState<string | null>(null);

  const handleSelect = async (email: string) => {
    setSelected(email);
    await messageAPI.markRead(email);
    refetch(); // 👈 cập nhật badge luôn
  };

  return (
    <div ref={dialogRef} className="chat-dialog">
      <ConversationList
        list={list}
        selected={selected}
        onSelect={handleSelect}
      />

      {selected ? (
        <MessagePanel otherEmail={selected} />
      ) : (
        <div className="empty-chat">
          Chọn một cuộc trò chuyện để bắt đầu
        </div>
      )}
    </div>
  );
};

export default ChatDialog;