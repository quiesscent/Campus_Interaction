
const { Op } = require('sequelize');
const Chat = require('../models/Chat');
const User = require('../models/User');
const Message = require('../models/Message');

// Create a new group chat
const createGroupChat = async (req, res) => {
    const { chatName, users } = req.body;

    if (!chatName || !users || users.length === 0) {
        return res.status(400).json({ message: 'Group chat name and users are required.' });
    }

    try {
        // Create the group chat with the requesting user as the admin
        const groupChat = await Chat.create({
            chatName,
            isGroupChat: true,
            adminId: req.user.id  // Requesting user is the group admin
        });

        // Add the requesting user and other users to the group
        await groupChat.setUsers([req.user.id, ...users]);

        res.status(201).json(groupChat);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Add a user to a group chat
const addUserToGroupChat = async (req, res) => {
    const { chatId, userId } = req.body;

    try {
        const groupChat = await Chat.findByPk(chatId);

        if (!groupChat || !groupChat.isGroupChat) {
            return res.status(404).json({ message: 'Group chat not found.' });
        }

        // Ensure that the requester is the admin of the group
        if (groupChat.adminId !== req.user.id) {
            return res.status(403).json({ message: 'Only the group admin can add users.' });
        }

        // Add the user to the group
        await groupChat.addUser(userId);

        res.status(200).json({ message: 'User added to the group chat.' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Remove a user from a group chat
const removeUserFromGroupChat = async (req, res) => {
    const { chatId, userId } = req.body;

    try {
        const groupChat = await Chat.findByPk(chatId);

        if (!groupChat || !groupChat.isGroupChat) {
            return res.status(404).json({ message: 'Group chat not found.' });
        }

        // Ensure that the requester is the admin of the group
        if (groupChat.adminId !== req.user.id) {
            return res.status(403).json({ message: 'Only the group admin can remove users.' });
        }

        // Remove the user from the group
        await groupChat.removeUser(userId);

        res.status(200).json({ message: 'User removed from the group chat.' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Change group chat name
const changeGroupName = async (req, res) => {
    const { chatId, newChatName } = req.body;

    if (!newChatName) {
        return res.status(400).json({ message: 'New chat name is required.' });
    }

    try {
        const groupChat = await Chat.findByPk(chatId);

        if (!groupChat || !groupChat.isGroupChat) {
            return res.status(404).json({ message: 'Group chat not found.' });
        }

        // Ensure that the requester is the admin of the group
        if (groupChat.adminId !== req.user.id) {
            return res.status(403).json({ message: 'Only the group admin can change the chat name.' });
        }

        // Update the chat name
        groupChat.chatName = newChatName;
        await groupChat.save();

        res.status(200).json({ message: 'Group chat name updated successfully.', groupChat });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Promote a user to group admin
const promoteToAdmin = async (req, res) => {
    const { chatId, newAdminId } = req.body;

    try {
        const groupChat = await Chat.findByPk(chatId);

        if (!groupChat || !groupChat.isGroupChat) {
            return res.status(404).json({ message: 'Group chat not found.' });
        }

        // Ensure that the requester is the current admin
        if (groupChat.adminId !== req.user.id) {
            return res.status(403).json({ message: 'Only the current admin can promote another user.' });
        }

        // Check if the new admin is a member of the group
        const isUserInGroup = await groupChat.hasUser(newAdminId);
        if (!isUserInGroup) {
            return res.status(400).json({ message: 'The user must be part of the group to be promoted to admin.' });
        }

        // Promote the user to admin
        groupChat.adminId = newAdminId;
        await groupChat.save();

        res.status(200).json({ message: 'User promoted to group admin.', groupChat });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Delete a group chat
const deleteGroupChat = async (req, res) => {
    const { chatId } = req.body;

    try {
        const groupChat = await Chat.findByPk(chatId);

        if (!groupChat || !groupChat.isGroupChat) {
            return res.status(404).json({ message: 'Group chat not found.' });
        }

        // Ensure that the requester is the admin of the group
        if (groupChat.adminId !== req.user.id) {
            return res.status(403).json({ message: 'Only the group admin can delete the chat.' });
        }

        // Delete the chat
        await groupChat.destroy();

        res.status(200).json({ message: 'Group chat deleted successfully.' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Get all members of a group chat
const getGroupMembers = async (req, res) => {
    const { chatId } = req.params;

    try {
        const groupChat = await Chat.findByPk(chatId, {
            include: [
                {
                    model: User,
                    as: 'users',
                    attributes: ['id', 'username', 'avatar'],
                    through: { attributes: [] }  // Omit join table details
                }
            ]
        });

        if (!groupChat || !groupChat.isGroupChat) {
            return res.status(404).json({ message: 'Group chat not found.' });
        }

        res.status(200).json(groupChat.users);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

module.exports = {
    createGroupChat,
    addUserToGroupChat,
    removeUserFromGroupChat,
    changeGroupName,
    promoteToAdmin,
    deleteGroupChat,
    getGroupMembers
};
