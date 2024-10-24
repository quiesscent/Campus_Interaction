
const express = require('express');
const router = express.Router();
const eventController = require('../controllers/eventController');
const { authenticate } = require('../middlewares/authMiddleware');

// Middleware to ensure user is authenticated
router.use(authenticate);

// Create a new event
router.post('/events', eventController.createEvent);

// Get details of a specific event
router.get('/events/:eventId', eventController.getEventDetails);

// RSVP for a specific event
router.post('/events/:eventId/rsvp', eventController.rsvpForEvent);

// Get all events
router.get('/events', eventController.getAllEvents);

// Delete a specific event
router.delete('/events/:eventId', eventController.deleteEvent);

module.exports = router;
