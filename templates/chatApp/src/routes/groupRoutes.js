
const express = require('express');
const router = express.Router();
const groupController = require('../controllers/groupController');
const { authenticate } = require('../middlewares/authMiddleware');

// Middleware to ensure user is authenticated
router.use(authenticate);

// Get a list of groups for the authenticated user
router.get('/groups', groupController.getUserGroups);

// Get details of a specific group
router.get('/groups/:groupId', groupController.getGroupDetails);

// Create a new group
router.post('/groups', groupController.createGroup);

// Add members to a group
router.post('/groups/:groupId/members', groupController.addMembersToGroup);

// Remove a member from a group
router.delete('/groups/:groupId/members/:userId', groupController.removeMemberFromGroup);

// Update group details
router.put('/groups/:groupId', groupController.updateGroup);

module.exports = router;
