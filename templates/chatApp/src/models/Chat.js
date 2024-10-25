
const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const Chat = sequelize.define('Chat', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true,
    },
    content: {
        type: DataTypes.TEXT,
        allowNull: false,
        validate: {
            len: {
                args: [1, 500],
                msg: 'Message content must be between 1 and 500 characters long.'
            },
        },
    },
    senderId: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: 'Users', // Assuming the Users table is named 'Users'
            key: 'id',
        },
        onDelete: 'CASCADE',
    },
    receiverId: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: 'Users', // Assuming the Users table is named 'Users'
            key: 'id',
        },
        onDelete: 'CASCADE',
    },
    isRead: {
        type: DataTypes.BOOLEAN,
        defaultValue: false,  // New messages are unread by default
    },
}, {
    // Options
    timestamps: true,  // Automatically manages createdAt and updatedAt
});

// Associations
Chat.associate = (models) => {
    Chat.belongsTo(models.User, { foreignKey: 'senderId', as: 'sender' });
    Chat.belongsTo(models.User, { foreignKey: 'receiverId', as: 'receiver' });
};

module.exports = Chat;
