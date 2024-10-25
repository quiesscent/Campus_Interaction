
const { Model, DataTypes } = require('sequelize');
const sequelize = require('../config/dbConfig'); 

class Message extends Model {}

Message.init({
    chatId: {
        type: DataTypes.INTEGER,
        allowNull: false,
    },
    senderId: {
        type: DataTypes.INTEGER,
        allowNull: false,
    },
    content: {
        type: DataTypes.TEXT,
        allowNull: false,
    },
    createdAt: {
        type: DataTypes.DATE,
        defaultValue: DataTypes.NOW,
    },
}, {
    sequelize,
    modelName: 'Message',
});

class Chat extends Model {}

Chat.init({
    title: {
        type: DataTypes.STRING,
        allowNull: false,
    },
    createdBy: {
        type: DataTypes.INTEGER,
        allowNull: false,
    },
}, {
    sequelize,
    modelName: 'Chat',
});
