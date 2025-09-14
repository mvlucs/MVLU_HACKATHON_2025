-- Audio & Video Translation System Database - SQLite3 Version
-- This file is now optional since the database is created automatically in app.py
-- But you can use it to initialize with sample data

-- Create translations table (will be created automatically by app.py)
CREATE TABLE IF NOT EXISTS translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    original_filename TEXT,
    source_language TEXT DEFAULT 'en',
    target_language TEXT NOT NULL,
    original_text TEXT,
    translated_text TEXT,
    audio_path TEXT,
    file_size INTEGER,
    processing_time REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_session ON translations(session_id);
CREATE INDEX IF NOT EXISTS idx_created ON translations(created_at);
CREATE INDEX IF NOT EXISTS idx_language ON translations(target_language);

-- Sample data for testing
INSERT OR IGNORE INTO translations (session_id, original_filename, target_language, original_text, translated_text)
VALUES
('sample-1', 'test.mp3', 'hi', 'Hello world', 'नमस्ते दुनिया'),
('sample-2', 'demo.wav', 'mr', 'Good morning', 'शुभ सकाळ'),
('sample-3', 'welcome.mp4', 'ta', 'Welcome to our system', 'எங்கள் அமைப்புக்கு வரவேற்கிறோம்');
