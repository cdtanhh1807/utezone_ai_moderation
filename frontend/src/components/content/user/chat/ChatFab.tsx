import React from 'react';
import ChatDialog from './ChatDialog';
import useConversations from './useConversation';

const ChatFab: React.FC = () => {
  const [open, setOpen] = React.useState(false);
  const { list, refetch } = useConversations();

  return (
    <>
      <button
        onClick={() => setOpen((o) => !o)}
        style={{
          position: 'fixed',
          bottom: 24,
          left: 24,
          width: 56,
          height: 56,
          borderRadius: '50%',
          border: 0,
          background: '#1976d2',
          color: '#fff',
          fontSize: 20,
          boxShadow: '0 3px 8px rgba(0,0,0,.25)',
          cursor: 'pointer',
          zIndex: 1000,
        }}
      >
        💬
      </button>

      {open && (
        <div
          style={{
            position: 'fixed',
            bottom: 90,
            left: 24,
            zIndex: 999,
          }}
        >
          <ChatDialog onClose={() => setOpen(false)} list={list} refetch={refetch} />
        </div>
      )}
    </>
  );
};

export default ChatFab;