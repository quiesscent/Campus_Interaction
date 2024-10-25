
const User = require('../models/User');
const Message = require('../models/Message');
const Chat = require('../models/Chat');

const { Sequelize } = require('sequelize');
require('dotenv').config(); // Load environment variables

// Create a new Sequelize instance and connect to SQLite
const sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: './database.sqlite', 
});

const connectDB = async () => {
    try {
        await sequelize.authenticate();
        console.log('Connection to SQLite has been established successfully.');
    } catch (error) {
        console.error('Unable to connect to the database:', error);
    }
};

// Sync all models with the database
const syncDB = async () => {
    try {
        await sequelize.sync({ alter: true }); 
        console.log("All models were synchronized successfully.");
    } catch (error) {
        console.error("Error synchronizing the database:", error);
    }
};

module.exports = { sequelize, connectDB, syncDB };
