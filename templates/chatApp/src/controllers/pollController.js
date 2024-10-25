
const { Poll, Option, Vote, User } = require('../models');  // Assuming models are defined in the project

// Create a new poll
const createPoll = async (req, res) => {
    try {
        const { question, options } = req.body;

        // Ensure that options are provided
        if (!options || options.length < 2) {
            return res.status(400).json({ message: 'A poll must have at least two options.' });
        }

        // Create the poll
        const poll = await Poll.create({
            question: question,
            createdBy: req.user.id  // Assuming req.user is populated with authenticated user data
        });

        // Create poll options
        const pollOptions = options.map(option => ({
            pollId: poll.id,
            text: option
        }));

        await Option.bulkCreate(pollOptions);

        res.status(201).json({ message: 'Poll created successfully.', poll });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Vote on a poll
const voteOnPoll = async (req, res) => {
    try {
        const { pollId, optionId } = req.body;
        const userId = req.user.id;

        // Check if the poll exists
        const poll = await Poll.findByPk(pollId, {
            include: [Option]
        });

        if (!poll) {
            return res.status(404).json({ message: 'Poll not found.' });
        }

        // Check if user has already voted on this poll
        const existingVote = await Vote.findOne({ where: { pollId, userId } });

        if (existingVote) {
            return res.status(400).json({ message: 'You have already voted on this poll.' });
        }

        // Record the vote
        await Vote.create({
            pollId,
            optionId,
            userId
        });

        res.status(201).json({ message: 'Vote recorded successfully.' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Get poll details (including votes)
const getPollDetails = async (req, res) => {
    try {
        const { pollId } = req.params;

        // Fetch poll, options, and votes
        const poll = await Poll.findByPk(pollId, {
            include: [
                {
                    model: Option,
                    include: [
                        {
                            model: Vote,
                            attributes: ['id', 'userId'] // Fetch votes for each option
                        }
                    ]
                }
            ]
        });

        if (!poll) {
            return res.status(404).json({ message: 'Poll not found.' });
        }

        // Format the result to include vote counts
        const formattedPoll = {
            id: poll.id,
            question: poll.question,
            options: poll.Options.map(option => ({
                id: option.id,
                text: option.text,
                votes: option.Votes.length
            })),
            totalVotes: poll.Options.reduce((sum, option) => sum + option.Votes.length, 0),
            createdBy: poll.createdBy
        };

        res.status(200).json(formattedPoll);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Delete a poll
const deletePoll = async (req, res) => {
    try {
        const { pollId } = req.params;
        const userId = req.user.id;

        // Fetch the poll to ensure it exists and the user is the owner
        const poll = await Poll.findByPk(pollId);

        if (!poll) {
            return res.status(404).json({ message: 'Poll not found.' });
        }

        // Ensure the user is the one who created the poll
        if (poll.createdBy !== userId) {
            return res.status(403).json({ message: 'You are not authorized to delete this poll.' });
        }

        // Delete the poll and associated options and votes
        await Option.destroy({ where: { pollId } });
        await Vote.destroy({ where: { pollId } });
        await poll.destroy();

        res.status(200).json({ message: 'Poll deleted successfully.' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

module.exports = {
    createPoll,
    voteOnPoll,
    getPollDetails,
    deletePoll
};
