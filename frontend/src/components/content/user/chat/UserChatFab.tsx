import React from 'react';
import ChatFab from './ChatFab';

const UserChatFab: React.FC = () => {
  const token = localStorage.getItem('token');
  if (!token) return null; // chưa login thì không render
  return <ChatFab />;
};

export default UserChatFab;