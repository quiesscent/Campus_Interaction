
const express = require('express');
const router = express.Router();
const mediaController = require('../controllers/mediaController');
const { authenticate } = require('../middlewares/authMiddleware');
const upload = require('../middlewares/uploadMiddleware'); // Middleware for handling file uploads

// Middleware to ensure user is authenticated
router.use(authenticate);

// Upload a new media file
router.post('/media/upload', upload.single('file'), mediaController.uploadMedia);

// Get a specific media file
router.get('/media/:mediaId', mediaController.getMedia);

// Delete a specific media file
router.delete('/media/:mediaId', mediaController.deleteMedia);

// Get all media files uploaded by a specific user
router.get('/media/user/:userId', mediaController.getUserMedia);

module.exports = router;
