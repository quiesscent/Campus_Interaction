
const Notification = require('../models/Notification');

// Create a new notification
const createNotification = async (userId, message) => {
    try {
        const notification = await Notification.create({ userId, message });
        return notification;
    } catch (error) {
        console.error('Error creating notification:', error);
        throw new Error('Unable to create notification.');
    }
};

// Fetch notifications for a specific user
const getNotificationsByUser = async (userId) => {
    try {
        const notifications = await Notification.findAll({
            where: { userId },
            order: [['createdAt', 'DESC']],
        });
        return notifications;
    } catch (error) {
        console.error('Error fetching notifications:', error);
        throw new Error('Unable to fetch notifications.');
    }
};

// Mark a notification as read
const markNotificationAsRead = async (notificationId) => {
    try {
        const notification = await Notification.findByPk(notificationId);
        if (!notification) {
            throw new Error('Notification not found.');
        }

        notification.isRead = true;
        await notification.save();
        return notification;
    } catch (error) {
        console.error('Error marking notification as read:', error);
        throw new Error('Unable to mark notification as read.');
    }
};

// Delete a notification
const deleteNotification = async (notificationId) => {
    try {
        const notification = await Notification.findByPk(notificationId);
        if (!notification) {
            throw new Error('Notification not found.');
        }

        await notification.destroy();
        return { message: 'Notification deleted successfully.' };
    } catch (error) {
        console.error('Error deleting notification:', error);
        throw new Error('Unable to delete notification.');
    }
};

module.exports = {
    createNotification,
    getNotificationsByUser,
    markNotificationAsRead,
    deleteNotification,
};
