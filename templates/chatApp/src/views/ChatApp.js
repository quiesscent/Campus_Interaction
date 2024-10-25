
import React, { useState } from 'react';
import ChatSidebar from './ChatSidebar';
import ChatWindow from './ChatWindow';

const ChatApp = () => {

  const [selectedChat, setSelectedChat] = useState(null);

  const handleSelectChat = (chat) => {
    setSelectedChat(chat);
  };

  return (
    <div className="container-fluid h-screen flex">
      {/* Sidebar for chat contacts */}
      <ChatSidebar onSelectChat={handleSelectChat} />

      {/* Main chat window */}
      {selectedChat ? (
        <ChatWindow chat={selectedChat} />
      ) : (
        <div className="col-md-9 d-flex align-items-center justify-content-center text-gray-500">
          <h4>Select a chat to start messaging</h4>
        </div>
      )}
    </div>
  );
};

export default ChatApp;
