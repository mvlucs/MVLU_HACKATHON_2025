#!/usr/bin/env python3
"""
Initialize SQLite database with sample data
Run this script if you want to manually set up the database
"""

import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'neuroforge.db'

def init_database():
    """Initialize SQLite database"""
    print("🔄 Initializing SQLite database...")
    
    try:
        # Remove existing database if it exists
        if os.path.exists(DATABASE_PATH):
            os.remove(DATABASE_PATH)
            print(f"🗑️  Removed existing database: {DATABASE_PATH}")
        
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()
        
        # Create translations table
        create_table = """
        CREATE TABLE translations (
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
        )
        """
        cursor.execute(create_table)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_session ON translations(session_id)")
        cursor.execute("CREATE INDEX idx_created ON translations(created_at)")
        cursor.execute("CREATE INDEX idx_language ON translations(target_language)")
        
        # Insert sample data
        sample_data = [
            ('sample-1', 'test.mp3', 'hi', 'Hello world', 'नमस्ते दुनिया'),
            ('sample-2', 'demo.wav', 'mr', 'Good morning', 'शुभ सकाळ'),
            ('sample-3', 'welcome.mp4', 'ta', 'Welcome to our system', 'எங்கள் அமைப்புக்கு வரவேற்கிறோம்'),
            ('sample-4', 'test.mp3', 'te', 'How are you?', 'మీరు ఎలా ఉన్నారు?'),
            ('sample-5', 'demo.wav', 'bn', 'Thank you', 'ধন্যবাদ')
        ]
        
        insert_query = """
        INSERT INTO translations (session_id, original_filename, target_language, original_text, translated_text)
        VALUES (?, ?, ?, ?, ?)
        """
        
        cursor.executemany(insert_query, sample_data)
        connection.commit()
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM translations")
        count = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        print(f"✅ Database initialized successfully!")
        print(f"📊 Created {count} sample translation records")
        print(f"📁 Database file: {os.path.abspath(DATABASE_PATH)}")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

if __name__ == "__main__":
    init_database()
