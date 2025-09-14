from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import sqlite3
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import uuid
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import processing functions
try:
    from audio_processing import audio_to_text, translate_text, text_to_speech, detect_language_from_audio
    PROCESSING_AVAILABLE = True
    logger.info("✅ Audio processing modules loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Audio processing modules not available: {e}")
    PROCESSING_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output_audio'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'avi', 'mov', 'm4a', 'ogg', 'webm', 'flac'}

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

# SQLite Database Configuration
DATABASE_PATH = 'neuroforge.db'

def get_db_connection():
    """Create SQLite database connection"""
    try:
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.Error as err:
        logger.error(f"Database connection failed: {err}")
        return None

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """Initialize SQLite database and create tables with migration support"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            # Create users table
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_users_table)
            
            # Check if translations table exists and has correct columns
            cursor.execute("PRAGMA table_info(translations)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            required_columns = [
                'id', 'session_id', 'original_filename', 'original_audio_path',
                'source_language', 'detected_source_language', 'target_language',
                'original_text', 'translated_text', 'audio_path', 'translated_audio_path',
                'translated_audio_url', 'file_size', 'processing_time',
                'confidence_score', 'voice_type', 'audio_duration', 'created_at'
            ]
            
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            if missing_columns or not existing_columns:
                # Backup existing data if table exists
                backup_data = []
                if existing_columns:
                    try:
                        cursor.execute("SELECT * FROM translations")
                        backup_data = cursor.fetchall()
                        logger.info(f"Backing up {len(backup_data)} existing translation records")
                    except:
                        pass
                
                # Drop and recreate table
                cursor.execute("DROP TABLE IF EXISTS translations")
                
                # Create new translations table with all required columns
                create_translations_table = """
                CREATE TABLE translations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    original_filename TEXT,
                    original_audio_path TEXT,
                    source_language TEXT DEFAULT 'en',
                    detected_source_language TEXT,
                    target_language TEXT,
                    original_text TEXT,
                    translated_text TEXT,
                    audio_path TEXT,
                    translated_audio_path TEXT,
                    translated_audio_url TEXT,
                    file_size INTEGER,
                    processing_time REAL,
                    confidence_score REAL DEFAULT 0.0,
                    voice_type TEXT DEFAULT 'standard',
                    audio_duration REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
                cursor.execute(create_translations_table)
                
                # Restore compatible data if any existed
                if backup_data and len(existing_columns) >= 12:
                    for row in backup_data:
                        try:
                            # Map old data to new structure with defaults for missing columns
                            insert_data = list(row[:12])  # Take first 12 columns that should exist
                            insert_data.extend([0.0, 'standard', 0.0])  # Add defaults for new columns
                            if len(row) > 12:
                                insert_data.append(row[-1])  # Keep original created_at if it exists
                            else:
                                insert_data.append(datetime.now().isoformat())
                            
                            placeholders = ','.join(['?' for _ in range(len(insert_data))])
                            cursor.execute(f"INSERT INTO translations VALUES (?, {placeholders})", insert_data)
                        except Exception as e:
                            logger.warning(f"Could not restore record: {e}")
                            continue
                
                logger.info(f"✅ Translations table recreated with {len(required_columns)} columns")
            else:
                logger.info("✅ Translations table already has correct structure")
            
            # Insert default users
            default_users = [
                ('superadmin@neuroforge.com', hash_password('super123'), 'Super Administrator', 'superadmin'),
                ('admin@neuroforge.com', hash_password('admin123'), 'Administrator', 'admin'),
                ('user@neuroforge.com', hash_password('user123'), 'Demo User', 'user')
            ]
            
            for email, password, name, role in default_users:
                cursor.execute("INSERT OR IGNORE INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
                             (email, password, name, role))
            
            connection.commit()
            cursor.close()
            connection.close()
            logger.info("✅ SQLite database initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # If all else fails, delete the database file and start fresh
        try:
            if os.path.exists(DATABASE_PATH):
                os.remove(DATABASE_PATH)
                logger.info("🔄 Database file deleted, will be recreated on next run")
        except:
            pass

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_comprehensive_language_support():
    """Get comprehensive list of supported languages for both input and output"""
    return {
        # Major World Languages with TTS Support
        'en': 'English',
        'es': 'Spanish (Español)',
        'fr': 'French (Français)', 
        'de': 'German (Deutsch)',
        'it': 'Italian (Italiano)',
        'pt': 'Portuguese (Português)',
        'pt-br': 'Portuguese Brazilian (Português Brasil)',
        'ru': 'Russian (Русский)',
        'ja': 'Japanese (日本語)',
        'ko': 'Korean (한국어)',
        'zh': 'Chinese Simplified (简体中文)',
        'zh-cn': 'Chinese Simplified (简体中文)',
        'zh-tw': 'Chinese Traditional (繁體中文)',
        'ar': 'Arabic (العربية)',
        'nl': 'Dutch (Nederlands)',
        'sv': 'Swedish (Svenska)',
        'no': 'Norwegian (Norsk)',
        'da': 'Danish (Dansk)',
        'fi': 'Finnish (Suomi)',
        'pl': 'Polish (Polski)',
        'cs': 'Czech (Čeština)',
        'sk': 'Slovak (Slovenčina)',
        'hu': 'Hungarian (Magyar)',
        'ro': 'Romanian (Română)',
        'bg': 'Bulgarian (Български)',
        'hr': 'Croatian (Hrvatski)',
        'sr': 'Serbian (Српски)',
        'sl': 'Slovenian (Slovenščina)',
        'et': 'Estonian (Eesti)',
        'lv': 'Latvian (Latviešu)',
        'lt': 'Lithuanian (Lietuvių)',
        'el': 'Greek (Ελληνικά)',
        'tr': 'Turkish (Türkçe)',
        'uk': 'Ukrainian (Українська)',
        'hi': 'Hindi (हिंदी)',
        'bn': 'Bengali (বাংলা)',
        'te': 'Telugu (తెలుగు)',
        'mr': 'Marathi (मराठी)',
        'ta': 'Tamil (தமிழ்)',
        'gu': 'Gujarati (ગુજરાતી)',
        'kn': 'Kannada (ಕನ್ನಡ)',
        'ml': 'Malayalam (മലയാളം)',
        'pa': 'Punjabi (ਪੰਜਾਬੀ)',
        'ur': 'Urdu (اردو)',
        'th': 'Thai (ไทย)',
        'vi': 'Vietnamese (Tiếng Việt)',
        'id': 'Indonesian (Bahasa Indonesia)',
        'ms': 'Malay (Bahasa Melayu)',
        'tl': 'Filipino (Tagalog)',
        'my': 'Myanmar (မြန်မာ)',
        'km': 'Khmer (ខ្មែរ)',
        'he': 'Hebrew (עברית)',
        'fa': 'Persian (فارسی)',
        'sw': 'Swahili (Kiswahili)',
        'af': 'Afrikaans',
        'is': 'Icelandic (Íslenska)',
        'ca': 'Catalan (Català)',
        'eu': 'Basque (Euskera)'
    }

def get_speech_recognition_lang_code(lang_code):
    """Map language codes to Speech Recognition compatible codes"""
    sr_mapping = {
        'en': 'en-US', 'es': 'es-ES', 'fr': 'fr-FR', 'de': 'de-DE', 'it': 'it-IT',
        'pt': 'pt-PT', 'pt-br': 'pt-BR', 'ru': 'ru-RU', 'ja': 'ja-JP', 'ko': 'ko-KR',
        'zh': 'zh-CN', 'zh-cn': 'zh-CN', 'zh-tw': 'zh-TW', 'ar': 'ar-SA',
        'nl': 'nl-NL', 'sv': 'sv-SE', 'no': 'nb-NO', 'da': 'da-DK', 'fi': 'fi-FI',
        'pl': 'pl-PL', 'cs': 'cs-CZ', 'sk': 'sk-SK', 'hu': 'hu-HU', 'ro': 'ro-RO',
        'bg': 'bg-BG', 'hr': 'hr-HR', 'sl': 'sl-SI', 'et': 'et-EE', 'lv': 'lv-LV',
        'lt': 'lt-LT', 'el': 'el-GR', 'tr': 'tr-TR', 'uk': 'uk-UA',
        'hi': 'hi-IN', 'bn': 'bn-IN', 'te': 'te-IN', 'mr': 'mr-IN', 'ta': 'ta-IN',
        'gu': 'gu-IN', 'kn': 'kn-IN', 'ml': 'ml-IN', 'pa': 'pa-IN', 'ur': 'ur-PK',
        'th': 'th-TH', 'vi': 'vi-VN', 'id': 'id-ID', 'ms': 'ms-MY', 'tl': 'tl-PH',
        'my': 'my-MM', 'km': 'km-KH', 'he': 'he-IL', 'fa': 'fa-IR', 'af': 'af-ZA',
        'sw': 'sw-KE', 'is': 'is-IS', 'ca': 'ca-ES', 'eu': 'eu-ES'
    }
    return sr_mapping.get(lang_code, f'{lang_code}-US')

def get_language_code_for_tts(lang_code):
    """Map language codes to TTS-compatible codes"""
    tts_mapping = {
        'zh': 'zh-cn', 'zh-cn': 'zh-cn', 'zh-tw': 'zh-tw', 'pt': 'pt', 'pt-br': 'pt-br'
    }
    return tts_mapping.get(lang_code, lang_code)

def get_audio_duration(file_path):
    """Get audio file duration in seconds"""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000.0  # Convert to seconds
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
        return 0.0

# Initialize database
init_database()

# Routes
@app.route('/')
def home():
    return jsonify({
        'status': 'success',
        'message': 'NeuroForge Voice Translation API Running!',
        'version': '5.0',
        'database': 'SQLite3 (neuroforge.db)',
        'processing_available': PROCESSING_AVAILABLE,
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'supported_languages': len(get_comprehensive_language_support()),
        'features': [
            'Universal Language Input Detection',
            'Multi-Language Output Support', 
            'High-Quality Voice Generation', 
            'Audio Playback Controls',
            'Audio Download & Streaming',
            'Real-time Voice Playback',
            'Multiple Voice Options'
        ]
    })

@app.route('/login')
def login_page():
    return send_from_directory('static', 'login.html')

@app.route('/signup')
def signup_page():
    return send_from_directory('static', 'signup.html')

@app.route('/translate')
def translate_page():
    return send_from_directory('static', 'translate.html')

@app.route('/register', methods=['POST'])
def register():
    """Handle user registration"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not email or not password or not name:
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
            
        if '@' not in email or '.' not in email:
            return jsonify({'success': False, 'error': 'Please enter a valid email address'}), 400
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                cursor.close()
                connection.close()
                return jsonify({'success': False, 'error': 'Email already registered'}), 400
            
            hashed_password = hash_password(password)
            cursor.execute(
                "INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
                (email, hashed_password, name, 'user')
            )
            user_id = cursor.lastrowid
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'message': 'Account created successfully!',
                'user': {'id': user_id, 'email': email, 'name': name, 'role': 'user'}
            })
        
        return jsonify({'success': False, 'error': 'Database error'}), 500
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'success': False, 'error': 'Registration failed'}), 500

@app.route('/auth', methods=['POST'])
def authenticate():
    """Handle login authentication"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            hashed_password = hash_password(password)
            cursor.execute(
                "SELECT id, email, name, role FROM users WHERE email = ? AND password = ?",
                (email, hashed_password)
            )
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if user:
                return jsonify({
                    'success': True,
                    'user': {
                        'id': user['id'], 'email': user['email'], 
                        'name': user['name'], 'role': user['role']
                    }
                })
            else:
                return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        
        return jsonify({'success': False, 'error': 'Database error'}), 500
            
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return jsonify({'success': False, 'error': 'Authentication failed'}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    start_time = datetime.now()
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        source_language = request.form.get('source_language', 'auto')
        target_language = request.form.get('target_language', 'en')
        voice_type = request.form.get('voice_type', 'standard')

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({
                'error': f'File type not supported. Allowed formats: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400

        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{session_id}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        file_size = os.path.getsize(file_path)
        logger.info(f"File saved: {unique_filename} ({file_size} bytes)")

        # Initialize variables
        original_text = ""
        translated_text = ""
        translated_audio_path = None
        translated_audio_url = None
        detected_source_lang = source_language
        confidence_score = 0.0
        audio_duration = 0.0

        # Process file with voice generation
        if PROCESSING_AVAILABLE:
            try:
                logger.info("Starting voice translation processing...")
                
                # Step 1: Language detection and text extraction
                if source_language == 'auto':
                    detection_attempts = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh-cn', 'ar', 'hi']
                    
                    best_result = None
                    best_confidence = 0.0
                    
                    for try_lang in detection_attempts:
                        try:
                            sr_lang = get_speech_recognition_lang_code(try_lang)
                            text_result = audio_to_text(file_path, src_lang=sr_lang)
                            
                            if text_result and not text_result.startswith('Could not') and len(text_result.strip()) > 5:
                                text_confidence = min(len(text_result.strip()) / 100.0, 1.0)
                                
                                if text_confidence > best_confidence:
                                    best_confidence = text_confidence
                                    best_result = text_result
                                    detected_source_lang = try_lang
                                    
                                if text_confidence > 0.8:
                                    break
                                    
                        except Exception as e:
                            continue
                    
                    if best_result:
                        original_text = best_result
                        confidence_score = best_confidence
                    else:
                        original_text = "Could not detect language or extract text from audio"
                        detected_source_lang = 'unknown'
                        confidence_score = 0.0
                        
                else:
                    sr_lang = get_speech_recognition_lang_code(source_language)
                    original_text = audio_to_text(file_path, src_lang=sr_lang)
                    detected_source_lang = source_language
                    confidence_score = 0.9
                
                logger.info(f"Speech-to-text completed ({detected_source_lang}): {original_text[:50]}...")
                
                # Step 2: Translation
                if detected_source_lang != target_language and detected_source_lang != 'unknown' and original_text and not original_text.startswith('Could not'):
                    translated_text = translate_text(
                        original_text, 
                        src_lang=detected_source_lang, 
                        target_lang=target_language
                    )
                    logger.info(f"Translation completed: {translated_text[:50]}...")
                elif detected_source_lang == target_language:
                    translated_text = original_text
                else:
                    translated_text = "Translation failed due to language detection issues"
                
                # Step 3: High-Quality Voice Generation
                if translated_text and not translated_text.startswith('Translation failed'):
                    try:
                        tts_lang_code = get_language_code_for_tts(target_language)
                        output_filename = f"voice_{session_id}.mp3"
                        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                        
                        # Enhanced TTS with voice options
                        translated_audio_path = text_to_speech(
                            text=translated_text,
                            lang=tts_lang_code,
                            out_file=output_path,
                            voice_type=voice_type
                        )
                        
                        if translated_audio_path and os.path.exists(translated_audio_path):
                            audio_duration = get_audio_duration(translated_audio_path)
                            translated_audio_url = f"/stream_audio/{session_id}"
                            logger.info(f"Voice generation completed: {translated_audio_path} ({audio_duration:.1f}s)")
                        
                    except Exception as e:
                        logger.error(f"Voice generation failed: {e}")
                        translated_audio_path = None
                
            except Exception as e:
                logger.error(f"Processing error: {e}")
                original_text = f"Processing failed for {filename}: {str(e)}"
                translated_text = f"Error: Could not process audio file"
                translated_audio_path = None
        else:
            # Mock response with voice simulation
            mock_texts = {
                'en': "This is sample English text extracted from the audio file.",
                'es': "Este es un texto de muestra en español extraído del archivo de audio.",
                'fr': "Ceci est un exemple de texte français extrait du fichier audio.",
                'de': "Dies ist ein Beispieltext auf Deutsch aus der Audiodatei.",
                'hi': "यह ऑडियो फाइल से निकाला गया हिंदी नमूना पाठ है।"
            }
            
            if source_language == 'auto':
                import random
                detected_source_lang = random.choice(['en', 'es', 'fr', 'de', 'hi'])
                confidence_score = random.uniform(0.7, 0.95)
            else:
                detected_source_lang = source_language
                confidence_score = 0.9
                
            original_text = mock_texts.get(detected_source_lang, mock_texts['en'])
            translated_text = get_sample_translation(target_language)
            
            # Generate mock voice audio (simplified fallback)
            try:
                output_filename = f"voice_{session_id}.mp3"
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                
                # Create a simple placeholder file for testing
                with open(output_path, 'w') as f:
                    f.write("Mock audio file")
                
                translated_audio_path = output_path
                audio_duration = 3.5  # Mock duration
                translated_audio_url = f"/stream_audio/{session_id}"
                logger.info(f"Mock voice generated: {translated_audio_path}")
            except Exception as e:
                logger.error(f"Mock voice generation failed: {e}")
                translated_audio_path = None

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Save to database with all required columns
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO translations
            (session_id, original_filename, original_audio_path, source_language, detected_source_language, 
             target_language, original_text, translated_text, audio_path, translated_audio_path, 
             translated_audio_url, file_size, processing_time, confidence_score, voice_type, audio_duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                session_id, filename, file_path, source_language, detected_source_lang, target_language,
                original_text, translated_text, file_path, translated_audio_path, 
                translated_audio_url, file_size, processing_time, confidence_score, 
                voice_type, audio_duration
            ))
            connection.commit()
            cursor.close()
            connection.close()

        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'original_text': original_text,
            'translated_text': translated_text,
            'source_language': source_language,
            'detected_source_language': detected_source_lang,
            'target_language': target_language,
            'confidence_score': confidence_score,
            'audio_available': translated_audio_path is not None,
            'audio_url': translated_audio_url,
            'audio_duration': audio_duration,
            'voice_type': voice_type,
            'processing_time': processing_time,
            'file_size': file_size,
            'download_url': f'/download_audio/{session_id}' if translated_audio_path else None
        })

    except Exception as e:
        logger.error(f"Upload processing failed: {e}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/stream_audio/<session_id>')
def stream_audio(session_id):
    """Stream audio file for real-time playback"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT translated_audio_path FROM translations WHERE session_id = ?",
                (session_id,)
            )
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if result and result['translated_audio_path'] and os.path.exists(result['translated_audio_path']):
                return send_file(
                    result['translated_audio_path'],
                    mimetype='audio/mpeg',
                    as_attachment=False,
                    conditional=True
                )
            else:
                return jsonify({'error': 'Audio file not found'}), 404
        
        return jsonify({'error': 'Database error'}), 500
        
    except Exception as e:
        logger.error(f"Audio streaming failed: {e}")
        return jsonify({'error': 'Streaming failed'}), 500

@app.route('/download_audio/<session_id>')
def download_audio(session_id):
    """Download the translated audio file"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT translated_audio_path, target_language, detected_source_language FROM translations WHERE session_id = ?",
                (session_id,)
            )
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if result and result['translated_audio_path'] and os.path.exists(result['translated_audio_path']):
                all_languages = get_comprehensive_language_support()
                source_lang_name = all_languages.get(result['detected_source_language'], 'Unknown')
                target_lang_name = all_languages.get(result['target_language'], 'Unknown')
                download_name = f"voice_translation_{source_lang_name}_to_{target_lang_name}_{session_id}.mp3"
                
                return send_file(
                    result['translated_audio_path'],
                    as_attachment=True,
                    download_name=download_name,
                    mimetype='audio/mpeg'
                )
            else:
                return jsonify({'error': 'Audio file not found'}), 404
        
        return jsonify({'error': 'Database error'}), 500
        
    except Exception as e:
        logger.error(f"Audio download failed: {e}")
        return jsonify({'error': 'Download failed'}), 500

def get_sample_translation(target_lang):
    """Get comprehensive sample translations for testing"""
    samples = {
        'hi': 'यह ऑडियो फाइल से निकाला गया नमूना पाठ है।',
        'es': 'Este es un texto de muestra extraído del archivo de audio.',
        'fr': 'Ceci est un exemple de texte extrait du fichier audio.',
        'de': 'Dies ist ein Beispieltext aus der Audiodatei.',
        'it': 'Questo è un testo di esempio estratto dal file audio.',
        'pt': 'Este é um texto de amostra extraído do arquivo de áudio.',
        'ru': 'Это образец текста, извлеченный из аудиофайла.',
        'ja': 'これは音声ファイルから抽出されたサンプルテキストです。',
        'ko': '이것은 오디오 파일에서 추출한 샘플 텍스트입니다.',
        'zh': '这是从音频文件中提取的示例文本。',
        'ar': 'هذا نص نموذجي مستخرج من ملف الصوت.',
        'th': 'นี่คือข้อความตัวอย่างที่แยกออกมาจากไฟล์เสียง',
        'vi': 'Đây là văn bản mẫu được trích xuất từ tệp âm thanh.',
        'id': 'Ini adalah contoh teks yang diekstrak dari file audio.',
        'nl': 'Dit is een voorbeeldtekst geëxtraheerd uit het audiobestand.',
        'sv': 'Detta är en exempeltext extraherad från ljudfilen.',
        'tr': 'Bu, ses dosyasından çıkarılan örnek bir metindir.',
        'pl': 'To jest przykładowy tekst wyodrębniony z pliku audio.',
        'cs': 'Toto je ukázkový text extrahovaný ze zvukového souboru.',
        'hu': 'Ez egy minta szöveg a hangfájlból kivonva.',
        'ro': 'Acesta este un text de probă extras din fișierul audio.'
    }
    return samples.get(target_lang, 'Sample translated text')

@app.route('/languages', methods=['GET'])
def get_languages():
    """Get all supported languages for output/target"""
    languages = get_comprehensive_language_support()
    return jsonify({
        'languages': languages,
        'total': len(languages)
    })

@app.route('/source_languages', methods=['GET'])
def get_source_languages():
    """Get all supported languages for input/source"""
    languages = get_comprehensive_language_support()
    ordered_languages = {'auto': '🌍 Auto-Detect Language'}
    ordered_languages.update(languages)
    return jsonify({
        'languages': ordered_languages,
        'total': len(ordered_languages)
    })

@app.route('/voice_options', methods=['GET'])
def get_voice_options():
    """Get available voice options"""
    voice_options = {
        'standard': 'Standard Voice',
        'slow': 'Slow Speech',
        'fast': 'Fast Speech'
    }
    return jsonify({
        'voice_options': voice_options,
        'default': 'standard'
    })

@app.route('/history', methods=['GET'])
def get_history():
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
            SELECT session_id, original_filename, source_language, detected_source_language, 
                   target_language, original_text, translated_text, translated_audio_url,
                   file_size, processing_time, confidence_score, voice_type, 
                   audio_duration, created_at
            FROM translations 
            ORDER BY created_at DESC 
            LIMIT 100
            """)
            
            history = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            connection.close()
            return jsonify({
                'history': history,
                'total': len(history)
            })
        
        return jsonify({'error': 'Database connection failed'}), 500
        
    except Exception as e:
        logger.error(f"History retrieval failed: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting NeuroForge Voice Translation API...")
    logger.info("📡 Available at: http://localhost:5000")
    logger.info(f"🗄️  Database: SQLite3 (neuroforge.db)")
    logger.info(f"🔧 Processing available: {PROCESSING_AVAILABLE}")
    logger.info(f"🌍 Supported languages: {len(get_comprehensive_language_support())}")
    logger.info("🔐 Login page: http://localhost:5000/login")
    logger.info("📝 Signup page: http://localhost:5000/signup")
    logger.info("🎵 Voice streaming: /stream_audio/<session_id>")
    logger.info("💾 Audio download: /download_audio/<session_id>")
    
    app.run(debug=True, host='0.0.0.0', port=5000)