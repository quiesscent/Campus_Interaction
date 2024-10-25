
const { createNotification } = require('../services/notificationService');

// Send a message and notify the recipient
const sendMessage = async (req, res) => {
    const { recipientId, content } = req.body;

    // Logic for sending message...
    
    // After sending the message, create a notification
    await createNotification(recipientId, `You have a new message from ${req.user.username}: "${content}"`);

    res.status(200).json({ message: 'Message sent and notification created.' });
};
