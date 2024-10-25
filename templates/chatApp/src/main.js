
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; 
import App from './App'; 

const root = ReactDOM.createRoot(document.getElementById('root'));

// Create a new React root
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const morgan = require('morgan');
const dotenv = require('dotenv');

// Load environment variables from .env file
dotenv.config();

const chatRoutes = require('./routes/chatRoutes');
const groupRoutes = require('./routes/groupRoutes');
const mediaRoutes = require('./routes/mediaRoutes');
const pollRoutes = require('./routes/pollRoutes');
const eventRoutes = require('./routes/eventRoutes');
const searchRoutes = require(',/routes/searchRoutes');

// Initialize the Express application
const app = express();

app.use(cors()); 
app.use(morgan('dev')); 
app.use(bodyParser.json()); 
app.use(bodyParser.urlencoded({ extended: true })); 

// Define routes
app.use('/api/auth', authRoutes);
app.use('/api/chats', chatRoutes);
app.use('/api/groups', groupRoutes);
app.use('/api/media', mediaRoutes);
app.use('/api/polls', pollRoutes);
app.use('/api/events', eventRoutes);

// Basic health check route
app.get('/', (req, res) => {
    res.status(200).send('Welcome to the CampHub API!');
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ message: 'Something went wrong!' });
});

// Start the server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
  
