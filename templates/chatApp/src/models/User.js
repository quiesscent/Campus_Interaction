
const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const User = sequelize.define('User', {
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
                msg: 'Name must be between 2 and 50 characters long.'
            },
        },
    },
    email: {
        type: DataTypes.STRING,
        allowNull: false,
        unique: {
            args: true,
            msg: 'Email address must be unique.'
        },
        validate: {
            isEmail: {
                msg: 'Please enter a valid email address.'
            },
            len: {
                args: [5, 100],
                msg: 'Email must be between 5 and 100 characters long.'
            },
        },
    },
    password: {
        type: DataTypes.STRING,
        allowNull: false,
        validate: {
            len: {
                args: [8, 100],
                msg: 'Password must be at least 8 characters long.'
            },
        },
    },
    profilePicture: {
        type: DataTypes.STRING,
        allowNull: true,  // Optional field
        validate: {
            isUrl: {
                msg: 'Profile picture must be a valid URL.'
            },
        },
    },
    bio: {
        type: DataTypes.TEXT,
        allowNull: true,  // Optional field
        validate: {
            len: {
                args: [0, 250],
                msg: 'Bio must be under 250 characters long.'
            },
        },
    },
}, {
    timestamps: true,  // Automatically manages createdAt and updatedAt
});

// Associations
User.associate = (models) => {
    // User can create many events
    User.hasMany(models.Event, { foreignKey: 'createdBy' });

    // User can attend many events through Attendance
    User.belongsToMany(models.Event, {
        through: models.Attendance,
        foreignKey: 'userId'
    });

    // User can send many messages
    User.hasMany(models.Message, { foreignKey: 'senderId', as: 'sentMessages' });

    // User can receive many messages
    User.hasMany(models.Message, { foreignKey: 'receiverId', as: 'receivedMessages' });

    // User can create many polls
    User.hasMany(models.Poll, { foreignKey: 'createdBy' });
};

// Hook to hash password before saving the user
User.beforeSave(async (user) => {
    if (user.changed('password')) {
        const hashedPassword = await bcrypt.hash(user.password, 10);
        user.password = hashedPassword;
    }
});

module.exports = User;
