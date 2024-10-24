
const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const Poll = sequelize.define('Poll', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true,
    },
    question: {
        type: DataTypes.STRING,
        allowNull: false,
        validate: {
            len: {
                args: [5, 255],
                msg: 'Question must be between 5 and 255 characters long.',
            },
        },
    },
    createdBy: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: 'Users', // Assuming the Users table is named 'Users'
            key: 'id',
        },
        onDelete: 'CASCADE',  // If the user is deleted, the poll will also be deleted
    },
    expiresAt: {
        type: DataTypes.DATE,
        allowNull: true, // Optional field
    },
}, {
    // Options
    timestamps: true,  // Automatically manages createdAt and updatedAt
});

// Associations
Poll.associate = (models) => {
    Poll.belongsTo(models.User, { foreignKey: 'createdBy' });
    Poll.hasMany(models.PollOption, { foreignKey: 'pollId', as: 'options' });
    Poll.hasMany(models.PollParticipation, { foreignKey: 'pollId', as: 'participations' });
};

module.exports = Poll;
