
const { Op } = require('sequelize');
const Chat = require('../models/Chat');
const Message = require('../models/Message');
const User = require('../models/User');

// Create a new chat (private or group)
const createChat = async (req, res) => {
    const { chatName, isGroupChat, users, adminId } = req.body;

    // Error handling: check if user data is valid
    if (!chatName || !users || users.length === 0) {
        return res.status(400).json({ message: 'Chat name and users are required.' });
    }

    try {
        const chat = await Chat.create({
            chatName,
            isGroupChat,
            adminId: isGroupChat ? adminId : null  // Admin is only relevant in group chats
        });

        if (isGroupChat) {
            await chat.setUsers(users);  // For group chats, associate users with the chat
        } else {
            await chat.setUsers([req.user.id, ...users]);  // Add requesting user and the target user(s) to the chat
        }

        res.status(201).json(chat);  // Return the newly created chat
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Fetch all chats for a specific user
const getUserChats = async (req, res) => {
    try {
        const chats = await Chat.findAll({
            where: {
                [Op.or]: [
                    { '$Users.id$': req.user.id }  
                ]
            },
            include: [
                {
                    model: User,
                    as: 'users',
                    attributes: ['id', 'username', 'avatar'],
                    through: { attributes: [] }  
                },
                {
                    model: Message,
                    attributes: ['content', 'createdAt'],
                    limit: 1,
                    order: [['createdAt', 'DESC']]  
                }
            ]
        });

        res.status(200).json(chats);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Send a message to a chat
const sendMessage = async (req, res) => {
    const { chatId, content, media } = req.body;

    if (!chatId || !content) {
        return res.status(400).json({ message: 'Chat ID and message content are required.' });
    }

    try {
        // Find the chat to send the message to
        const chat = await Chat.findByPk(chatId);
        if (!chat) {
            return res.status(404).json({ message: 'Chat not found.' });
        }

        // Create a new message in the chat
        const message = await Message.create({
            senderId: req.user.id,  // ID of the user sending the message
            chatId,
            content,
            media  // Optional media attachment
        });

        // Update the chat's latest message reference
        await chat.update({ latestMessage: message.id });

        res.status(201).json(message);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

const getChatMessages = async (req, res) => {
    const { chatId } = req.params;

    try {
        
        const messages = await Message.findAll({
            where: { chatId },
            include: [
                {
                    model: User,
                    as: 'sender',
                    attributes: ['id', 'username', 'avatar']
                }
            ],
            order: [['createdAt', 'ASC']]  // Order messages by creation date
        });

        res.status(200).json(messages);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Mark messages as read in a chat
const markMessagesAsRead = async (req, res) => {
    const { chatId } = req.body;

    try {
        // Mark all unread messages as read
        await Message.update(
            { seen: true },
            {
                where: {
                    chatId,
                    seen: false,
                    senderId: { [Op.ne]: req.user.id }                  }
            }
        );

        res.status(200).json({ message: 'Messages marked as read.' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Remove a user from a group chat
const removeUserFromGroupChat = async (req, res) => {
    const { chatId, userId } = req.body;

    try {
        const chat = await Chat.findByPk(chatId);

        if (!chat || !chat.isGroupChat) {
            return res.status(404).json({ message: 'Group chat not found.' });
        }

        // Ensure that the requesting user is the admin of the group
        if (chat.adminId !== req.user.id) {
            return res.status(403).json({ message: 'Only the group admin can remove users.' });
        }

        // Remove the specified user from the chat
        await chat.removeUser(userId);
        res.status(200).json({ message: 'User removed from the group chat.' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Add a user to a group chat
const addUserToGroupChat = async (req, res) => {
    const { chatId, userId } = req.body;

    try {
        const chat = await Chat.findByPk(chatId);

        if (!chat || !chat.isGroupChat) {
            return res.status(404).json({ message: 'Group chat not found.' });
        }

        // Ensure that the requesting user is the admin of the group
        if (chat.adminId !== req.user.id) {
            return res.status(403).json({ message: 'Only the group admin can add users.' });
        }

        // Add the specified user to the chat
        await chat.addUser(userId);
        res.status(200).json({ message: 'User added to the group chat.' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

module.exports = {
    createChat,
    getUserChats,
    sendMessage,
    getChatMessages,
    markMessagesAsRead,
    removeUserFromGroupChat,
    addUserToGroupChat
};
// controllers/chatController.js


