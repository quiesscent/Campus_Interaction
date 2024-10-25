
const { searchAll } = require('../services/searchService');

// Search messages and chats
const search = async (req, res) => {
    const { keyword, participantUsername } = req.query; 

    try {
        const results = await searchAll(req.user.id, keyword, participantUsername);
        res.status(200).json(results);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

module.exports = {
    search,
};
