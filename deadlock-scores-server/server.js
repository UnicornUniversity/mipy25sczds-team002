const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;
const DB_PATH = path.join(__dirname, 'scores.db');

// Middleware
app.use(helmet());
app.use(cors({
    origin: ['http://localhost', 'http://127.0.0.1', 'https://yourdomain.com'],
    methods: ['GET', 'POST'],
    credentials: true
}));
app.use(bodyParser.json({ limit: '1mb' }));

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP'
});
app.use('/api/', limiter);

// Stricter rate limiting for POST requests
const postLimiter = rateLimit({
    windowMs: 60 * 1000, // 1 minute
    max: 5, // limit each IP to 5 POST requests per minute
    message: 'Too many score submissions from this IP'
});

// Database initialization
const db = new sqlite3.Database(DB_PATH, (err) => {
    if (err) {
        console.error('Error opening database:', err.message);
    } else {
        console.log('Connected to SQLite database');
        // Create scores table if it doesn't exist
        db.run(`CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL,
            date TEXT NOT NULL,
            game TEXT DEFAULT 'deadlock',
            ip_address TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);
    }
});

// Input validation middleware
const validateScoreInput = (req, res, next) => {
    const { name, score, date } = req.body;

    // Validate name
    if (!name || typeof name !== 'string' || name.trim().length === 0) {
        return res.status(400).json({ error: 'Valid name is required' });
    }
    if (name.length > 50) {
        return res.status(400).json({ error: 'Name too long (max 50 characters)' });
    }

    // Validate score
    if (typeof score !== 'number' || score < 0 || score > 999999999) {
        return res.status(400).json({ error: 'Valid score is required (0-999999999)' });
    }

    // Validate date
    if (!date || typeof date !== 'string') {
        return res.status(400).json({ error: 'Valid date is required' });
    }

    // Sanitize name (remove special characters)
    req.body.name = name.trim().replace(/[<>\"'&]/g, '');

    next();
};

// Routes

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Get scores (with pagination)
app.get('/api/scores', (req, res) => {
    const limit = Math.min(parseInt(req.query.limit) || 10, 100); // Max 100 scores
    const offset = parseInt(req.query.offset) || 0;
    const game = req.query.game || 'deadlock';

    const query = `
        SELECT name, score, date 
        FROM scores 
        WHERE game = ? 
        ORDER BY score DESC, created_at ASC 
        LIMIT ? OFFSET ?
    `;

    db.all(query, [game, limit, offset], (err, rows) => {
        if (err) {
            console.error('Database error:', err);
            res.status(500).json({ error: 'Database error' });
        } else {
            res.json(rows);
        }
    });
});

// Submit new score
app.post('/api/scores', postLimiter, validateScoreInput, (req, res) => {
    const { name, score, date } = req.body;
    const game = req.body.game || 'deadlock';
    const ip_address = req.ip || req.connection.remoteAddress;

    const query = `
        INSERT INTO scores (name, score, date, game, ip_address) 
        VALUES (?, ?, ?, ?, ?)
    `;

    db.run(query, [name, score, date, game, ip_address], function(err) {
        if (err) {
            console.error('Database error:', err);
            res.status(500).json({ error: 'Failed to save score' });
        } else {
            console.log(`New score submitted: ${name} - ${score} points`);
            res.json({
                success: true,
                message: 'Score saved successfully',
                id: this.lastID
            });
        }
    });
});

// Get server stats (optional)
app.get('/api/stats', (req, res) => {
    const game = req.query.game || 'deadlock';

    db.get(`
        SELECT 
            COUNT(*) as total_scores,
            MAX(score) as highest_score,
            AVG(score) as average_score
        FROM scores 
        WHERE game = ?
    `, [game], (err, row) => {
        if (err) {
            console.error('Database error:', err);
            res.status(500).json({ error: 'Database error' });
        } else {
            res.json(row);
        }
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Unhandled error:', err);
    res.status(500).json({ error: 'Internal server error' });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: 'Endpoint not found' });
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('Shutting down server...');
    db.close((err) => {
        if (err) {
            console.error('Error closing database:', err.message);
        } else {
            console.log('Database connection closed.');
        }
        process.exit(0);
    });
});

app.listen(PORT, '127.0.0.1', () => {
    console.log(`Deadlock Scores Server running on port ${PORT}`);
    console.log(`Database: ${DB_PATH}`);
});