
const express = require('express');
const router = express.Router();
const chatController = require('../controllers/chatController');
const { authenticate } = require('../middlewares/authMiddleware');

// Middleware to ensure user is authenticated
router.use(authenticate);

// Get a list of chats for the authenticated user
router.get('/chats', chatController.getUserChats);

// Get messages from a specific chat
router.get('/chats/:chatId', chatController.getChatMessages);

// Create a new chat
router.post('/chats', chatController.createChat);

// Send a message to a specific chat
router.post('/chats/:chatId/messages', chatController.sendMessage);

// Create a new group chat
router.post('/chats/:chatId/groups', chatController.createGroupChat);

// React to a specific message
router.post('/chats/:chatId/messages/:messageId/react', chatController.reactToMessage);

module.exports = router;
