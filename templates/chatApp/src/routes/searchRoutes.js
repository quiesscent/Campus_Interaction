
const express = require('express');
const router = express.Router();
const searchController = require('../controllers/searchController');
const { authenticate } = require('../middlewares/authMiddleware');

// Middleware to ensure user is authenticated
router.use(authenticate);

// Search messages and chats
router.get('/search', searchController.search);

module.exports = router;
