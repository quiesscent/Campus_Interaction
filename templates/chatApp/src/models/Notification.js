
const { DataTypes } = require('sequelize');
const sequelize = require('../config/dbConfig'); // Assuming you have this configured

const Notification = sequelize.define('Notification', {
    userId: {
        type: DataTypes.INTEGER,
        allowNull: false,
    },
    message: {
        type: DataTypes.STRING,
        allowNull: false,
    },
    isRead: {
        type: DataTypes.BOOLEAN,
        defaultValue: false,
    },
    createdAt: {
        type: DataTypes.DATE,
        defaultValue: DataTypes.NOW,
    },
});

module.exports = Notification;
