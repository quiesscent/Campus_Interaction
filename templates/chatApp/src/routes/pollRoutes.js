
const express = require('express');
const router = express.Router();
const pollController = require('../controllers/pollController');
const { authenticate } = require('../middlewares/authMiddleware');

// Middleware to ensure user is authenticated
router.use(authenticate);

// Create a new poll
router.post('/polls', pollController.createPoll);

// Get details of a specific poll
router.get('/polls/:pollId', pollController.getPollDetails);

// Vote on a specific poll
router.post('/polls/:pollId/vote', pollController.voteOnPoll);

// Get all polls
router.get('/polls', pollController.getAllPolls);

// Delete a specific poll
router.delete('/polls/:pollId', pollController.deletePoll);

module.exports = router;
