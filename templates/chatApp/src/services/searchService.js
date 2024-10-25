
const { Message, Chat } = require('../models');

// Search messages based on keywords
const searchMessages = async (userId, keyword) => {
    try {
        const messages = await Message.findAll({
            where: {
                content: {
                    [Op.like]: `%${keyword}%`
                },
            },
            include: [
                {
                    model: Chat,
                    as: 'chat',
                    required: true,
                },
            ],
            order: [['createdAt', 'DESC']],
        });
        return messages;
    } catch (error) {
        console.error('Error searching messages:', error);
        throw new Error('Unable to search messages.');
    }
};

// Search chats based on participant usernames
const searchChats = async (userId, participantUsername) => {
    try {
        const chats = await Chat.findAll({
            where: {
                
                [Op.or]: [
                    { '$participants.username$': { [Op.like]: `%${participantUsername}%` } },
                ],
            },
            include: [
                {
                    model: User, 
                    as: 'participants',
                    required: true,
                },
            ],
            order: [['createdAt', 'DESC']],
        });
        return chats;
    } catch (error) {
        console.error('Error searching chats:', error);
        throw new Error('Unable to search chats.');
    }
};

const searchAll = async (userId, keyword, participantUsername) => {
    try {
        const messages = await searchMessages(userId, keyword);
        const chats = await searchChats(userId, participantUsername);

        return {
            messages,
            chats,
        };
    } catch (error) {
        console.error('Error searching:', error);
        throw new Error('Unable to perform search.');
    }
};

module.exports = {
    searchMessages,
    searchChats,
    searchAll,
};
