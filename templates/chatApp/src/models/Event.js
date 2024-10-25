
const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const Event = sequelize.define('Event', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true,
    },
    title: {
        type: DataTypes.STRING,
        allowNull: false,
        validate: {
            len: {
                args: [5, 100],
                msg: 'Title must be between 5 and 100 characters long.',
            },
        },
    },
    description: {
        type: DataTypes.TEXT,
        allowNull: true,
    },
    location: {
        type: DataTypes.STRING,
        allowNull: false,
    },
    startTime: {
        type: DataTypes.DATE,
        allowNull: false,
    },
    endTime: {
        type: DataTypes.DATE,
        allowNull: false,
        validate: {
            isAfter(value) {
                if (new Date(value) <= new Date(this.startTime)) {
                    throw new Error('End time must be after start time.');
                }
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
        onDelete: 'CASCADE',  // If the user is deleted, the event will also be deleted
    },
}, {
    // Options
    timestamps: true,  
});

// Associations
Event.associate = (models) => {
    Event.belongsTo(models.User, { foreignKey: 'createdBy' });
    Event.hasMany(models.EventParticipation, { foreignKey: 'eventId', as: 'participations' });
};

module.exports = Event;
