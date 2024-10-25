
import React, { useState } from 'react';

const MessageInput = ({ onSendMessage }) => {
  const [messageText, setMessageText] = useState('');

  const handleInputChange = (e) => {
    setMessageText(e.target.value);
  };

  const handleSend = () => {
    onSendMessage(messageText);
    setMessageText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="p-3 border-top bg-light d-flex align-items-center">
      <input
        type="text"
        className="form-control me-3"
        placeholder="Type a message..."
        value={messageText}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
      />
      <button className="btn btn-primary" onClick={handleSend}>
        Send
      </button>
    </div>
  );
};

export default MessageInput;
