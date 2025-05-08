import React from 'react';

const ChatBubble = ({ from, text }) => {
  const isUser = from === 'user';
  return (
    <div className={`chat-bubble ${isUser ? 'user' : from}`}>
      <p>{text}</p>
    </div>
  );
};

export default ChatBubble;