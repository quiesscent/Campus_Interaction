
const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const Media = sequelize.define('Media', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true,
    },
    url: {
        type: DataTypes.STRING,
        allowNull: false,
        validate: {
            isUrl: {
                msg: 'Must be a valid URL.'
            },
        },
    },
    type: {
        type: DataTypes.ENUM('image', 'video', 'document'), // Define the acceptable types of media
        allowNull: false,
    },
    uploadedBy: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: 'Users', // Assuming the Users table is named 'Users'
            key: 'id',
        },
        onDelete: 'CASCADE',  // If the user is deleted, associated media will also be deleted
    },
    chatId: {
        type: DataTypes.INTEGER,
        allowNull: true,
        references: {
            model: 'Chats', // Assuming the Chats table is named 'Chats'
            key: 'id',
        },
        onDelete: 'CASCADE',  // If the chat is deleted, associated media will also be deleted
    },
}, {
    // Options
    timestamps: true,  
});

// Associations
Media.associate = (models) => {
    Media.belongsTo(models.User, { foreignKey: 'uploadedBy' });
    Media.belongsTo(models.Chat, { foreignKey: 'chatId', allowNull: true });
};

module.exports = Media;
