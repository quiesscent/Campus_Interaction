
import React, { useState } from 'react';
import MessageInput from './MessageInput';

const ChatWindow = ({ chat }) => {
  const [messages, setMessages] = useState([
    { id: 1, sender: 'John Doe', content: 'Hey, how are you?', timestamp: '2:30 PM' },
    { id: 2, sender: 'Me', content: 'I\'m doing great, thanks!', timestamp: '2:31 PM' },
  ]);

  const handleSendMessage = (messageText) => {
    if (messageText.trim()) {
      const newMessage = {
        id: messages.length + 1,
        sender: 'Me',
        content: messageText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages([...messages, newMessage]);
    }
  };

  return (
    <div className="col-md-9 d-flex flex-column bg-white">
      {/* Chat Header */}
      <div className="p-3 border-bottom bg-light">
        <h6 className="font-weight-bold mb-0">{chat.name}</h6>
      </div>

      {/* Chat Messages */}
      <div className="flex-grow-1 p-3 overflow-auto" style={{ maxHeight: '70vh' }}>
        {messages.map((message) => (
          <div
            key={message.id}
            className={`d-flex mb-3 ${message.sender === 'Me' ? 'justify-content-end' : ''}`}
          >
            <div
              className={`p-2 rounded ${message.sender === 'Me' ? 'bg-primary text-white' : 'bg-light text-dark'}`}
              style={{ maxWidth: '75%' }}
            >
              <p className="mb-1">{message.content}</p>
              <small className="text-muted">{message.timestamp}</small>
            </div>
          </div>
        ))}
      </div>

      {/* Message Input */}
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  );
};

export default ChatWindow;
