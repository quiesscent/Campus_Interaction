
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { Media } = require('../models');  

// Set up storage engine for Multer
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        const uploadPath = path.join(__dirname, '../uploads/');
        if (!fs.existsSync(uploadPath)) {
            fs.mkdirSync(uploadPath, { recursive: true });
        }
        cb(null, uploadPath);
    },
    filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        const ext = path.extname(file.originalname);
        cb(null, file.fieldname + '-' + uniqueSuffix + ext);
    }
});

// File filter function to restrict the file types
const fileFilter = (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif|mp4|mkv|avi|pdf|doc|docx/;
    const mimeType = allowedTypes.test(file.mimetype);
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());

    if (mimeType && extname) {
        return cb(null, true);
    } else {
        cb(new Error('File type not supported.'));
    }
};

// Multer configuration
const upload = multer({
    storage: storage,
    limits: { fileSize: 10 * 1024 * 1024 }, // 10MB file size limit
    fileFilter: fileFilter
});

// Upload media file
const uploadMedia = async (req, res) => {
    try {
        const file = req.file;
        if (!file) {
            return res.status(400).json({ message: 'No file uploaded.' });
        }

        // Store file metadata in the database
        const newMedia = await Media.create({
            filename: file.filename,
            filepath: file.path,
            mimetype: file.mimetype,
            size: file.size,
            uploadedBy: req.user.id
        });

        res.status(201).json({ message: 'File uploaded successfully.', media: newMedia });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Get all media files
const getAllMedia = async (req, res) => {
    try {
        const mediaFiles = await Media.findAll({
            attributes: ['id', 'filename', 'filepath', 'mimetype', 'size', 'createdAt'],
            where: { uploadedBy: req.user.id }
        });

        res.status(200).json(mediaFiles);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Get a specific media file by ID
const getMediaById = async (req, res) => {
    try {
        const { mediaId } = req.params;
        const media = await Media.findByPk(mediaId);

        if (!media) {
            return res.status(404).json({ message: 'Media not found.' });
        }

        res.status(200).json(media);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Download media file
const downloadMedia = async (req, res) => {
    try {
        const { mediaId } = req.params;
        const media = await Media.findByPk(mediaId);

        if (!media) {
            return res.status(404).json({ message: 'Media not found.' });
        }

        res.download(media.filepath, media.filename);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Delete media file
const deleteMedia = async (req, res) => {
    try {
        const { mediaId } = req.params;
        const media = await Media.findByPk(mediaId);

        if (!media) {
            return res.status(404).json({ message: 'Media not found.' });
        }

        // Remove file from the filesystem
        fs.unlinkSync(media.filepath);

        // Remove the media entry from the database
        await media.destroy();

        res.status(200).json({ message: 'Media deleted successfully.' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

module.exports = {
    uploadMedia,
    getAllMedia,
    getMediaById,
    downloadMedia,
    deleteMedia
};
