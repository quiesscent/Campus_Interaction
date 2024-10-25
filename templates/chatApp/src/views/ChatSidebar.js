
import React from 'react';

const ChatSidebar = ({ onSelectChat }) => {
  const chats = [
    { id: 1, name: 'John Doe', lastMessage: 'Hey, how are you?' },
    { id: 2, name: 'Jane Smith', lastMessage: 'You: I\'ll call you later' },
    { id: 3, name: 'Alice Johnson', lastMessage: 'Did you see the news?' },
  ];

  return (
    <div className="col-md-3 border-right bg-light p-4 overflow-auto">
      <h5 className="text-lg font-semibold mb-4">Chats</h5>

      {/* Search Bar */}
      <div className="mb-4">
        <input type="text" className="form-control" placeholder="Search chats..." />
      </div>

      {/* Chat list */}
      <div>
        {chats.map((chat) => (
          <div
            key={chat.id}
            className="d-flex align-items-center p-3 border-bottom hover:bg-light cursor-pointer"
            onClick={() => onSelectChat(chat)}
          >
            <img
              src="https://via.placeholder.com/40"
              className="rounded-circle me-3"
              alt="User Avatar"
            />
            <div>
              <h6 className="font-weight-bold">{chat.name}</h6>
              <p className="text-sm text-muted mb-0">{chat.lastMessage}</p>
            </div>
            <span className="ms-auto text-xs text-muted">2:30 PM</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatSidebar;
