
const nodemailer = require('nodemailer');

// Configure the transporter
const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST || 'smtp.example.com', 
    port: process.env.SMTP_PORT || 587, 
    secure: process.env.SMTP_SECURE || false, 
    auth: {
        user: process.env.SMTP_USER || 'your_email@example.com', 
        pass: process.env.SMTP_PASS || 'your_password', 
    },
});

// Function to send email
const sendEmail = async (to, subject, text, html) => {
    try {
        const mailOptions = {
            from: process.env.SMTP_FROM || 'your_email@example.com', 
            to,
            subject,
            text,
            html,
        };

        const info = await transporter.sendMail(mailOptions);
        console.log('Email sent: ', info.response);
    } catch (error) {
        console.error('Error sending email:', error);
        throw new Error('Unable to send email.');
    }
};

// Function to send a welcome email
const sendWelcomeEmail = async (userEmail, userName) => {
    const subject = 'Welcome to Our Social Network!';
    const text = `Hi ${userName},\n\nThank you for joining our platform! We are excited to have you.\n\nBest Regards,\nThe Team`;
    const html = `<p>Hi ${userName},</p><p>Thank you for joining our platform! We are excited to have you.</p><p>Best Regards,<br>The Team</p>`;

    await sendEmail(userEmail, subject, text, html);
};

// Function to send a password reset email
const sendPasswordResetEmail = async (userEmail, resetLink) => {
    const subject = 'Password Reset Request';
    const text = `You requested a password reset. Click the link below to reset your password:\n\n${resetLink}`;
    const html = `<p>You requested a password reset. Click the link below to reset your password:</p><p><a href="${resetLink}">Reset Password</a></p>`;

    await sendEmail(userEmail, subject, text, html);
};

module.exports = {
    sendEmail,
    sendWelcomeEmail,
    sendPasswordResetEmail,
};
