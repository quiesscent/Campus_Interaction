
const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const Group = sequelize.define('Group', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true,
    },
    name: {
        type: DataTypes.STRING,
        allowNull: false,
        validate: {
            len: {
                args: [2, 50],
                msg: 'Group name must be between 2 and 50 characters long.'
            },
        },
    },
    description: {
        type: DataTypes.TEXT,
        allowNull: true,  // Optional field
        validate: {
            len: {
                args: [0, 250],
                msg: 'Description must be under 250 characters long.'
            },
        },
    },
    adminId: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: 'Users', // Assuming the Users table is named 'Users'
            key: 'id',
        },
        onDelete: 'SET NULL',  // If admin is deleted, set the adminId to NULL
    },
}, {
    // Options
    timestamps: true,  // Automatically manages createdAt and updatedAt
});

// Associations
Group.associate = (models) => {
    // A group can have many members (Users)
    Group.belongsToMany(models.User, {
        through: models.GroupMembership, // Assuming a join table called GroupMembership
        foreignKey: 'groupId',
        as: 'members',
    });

    // A group can have many events
    Group.hasMany(models.Event, { foreignKey: 'groupId' });
};

module.exports = Group;
