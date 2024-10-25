
const { Event, User, Attendance } = require('../models');  

// Create a new event
const createEvent = async (req, res) => {
    try {
        const { title, description, date, location } = req.body;

        // Create the event
        const event = await Event.create({
            title,
            description,
            date,
            location,
            createdBy: req.user.id  // Assuming req.user is populated with authenticated user data
        });

        res.status(201).json({ message: 'Event created successfully.', event });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Register user for an event
const registerForEvent = async (req, res) => {
    try {
        const { eventId } = req.body;
        const userId = req.user.id;

        // Check if the event exists
        const event = await Event.findByPk(eventId);

        if (!event) {
            return res.status(404).json({ message: 'Event not found.' });
        }

        // Check if the user is already registered
        const existingRegistration = await Attendance.findOne({ where: { eventId, userId } });

        if (existingRegistration) {
            return res.status(400).json({ message: 'You are already registered for this event.' });
        }

        // Register the user for the event
        await Attendance.create({ eventId, userId });

        res.status(201).json({ message: 'Successfully registered for the event.' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Get event details (including attendees)
const getEventDetails = async (req, res) => {
    try {
        const { eventId } = req.params;

        // Fetch event and attendees
        const event = await Event.findByPk(eventId, {
            include: [{
                model: User,
                through: { attributes: [] } // Exclude the join table attributes
            }]
        });

        if (!event) {
            return res.status(404).json({ message: 'Event not found.' });
        }

        const formattedEvent = {
            id: event.id,
            title: event.title,
            description: event.description,
            date: event.date,
            location: event.location,
            createdBy: event.createdBy,
            attendees: event.Users.map(user => ({
                id: user.id,
                name: user.name,
                email: user.email
            })),
            totalAttendees: event.Users.length
        };

        res.status(200).json(formattedEvent);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Delete an event
const deleteEvent = async (req, res) => {
    try {
        const { eventId } = req.params;
        const userId = req.user.id;

        // Fetch the event to ensure it exists and the user is the owner
        const event = await Event.findByPk(eventId);

        if (!event) {
            return res.status(404).json({ message: 'Event not found.' });
        }

        // Ensure the user is the one who created the event
        if (event.createdBy !== userId) {
            return res.status(403).json({ message: 'You are not authorized to delete this event.' });
        }

        // Delete the event and associated registrations
        await Attendance.destroy({ where: { eventId } });
        await event.destroy();

        res.status(200).json({ message: 'Event deleted successfully.' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

module.exports = {
    createEvent,
    registerForEvent,
    getEventDetails,
    deleteEvent
};
