import os
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from pydub import AudioSegment
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FFmpeg Configuration (update paths as needed)
ffmpeg_path = r"C:\Users\itlab\Downloads\ffmpeg-2025-09-10-git-c1dc2e2b7c-essentials_build\ffmpeg-2025-09-10-git-c1dc2e2b7c-essentials_build\bin\ffmpeg.exe"
ffprobe_path = r"C:\Users\itlab\Downloads\ffmpeg-2025-09-10-git-c1dc2e2b7c-essentials_build\ffmpeg-2025-09-10-git-c1dc2e2b7c-essentials_build\bin\ffprobe.exe"

if os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path):
    os.environ["PATH"] = os.path.dirname(ffmpeg_path) + ";" + os.environ["PATH"]
    os.environ["PATH"] = os.path.dirname(ffprobe_path) + ";" + os.environ["PATH"]
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffprobe = ffprobe_path
    logger.info("✅ FFmpeg configured successfully")
else:
    logger.warning("⚠️ FFmpeg not found. Audio conversion may fail.")

# Initialize recognizer with optimized settings
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8
recognizer.operation_timeout = None
recognizer.phrase_timeout = None
recognizer.non_speaking_duration = 0.5

def audio_to_text(file_path, src_lang="en-US"):
    """Enhanced audio to text conversion"""
    temp_files = []
    
    try:
        wav_file = f"temp_{os.path.basename(file_path)}.wav"
        temp_files.append(wav_file)
        
        file_format = os.path.splitext(file_path)[1][1:].lower()
        
        # Enhanced audio preprocessing
        audio = AudioSegment.from_file(file_path, format=file_format)
        
        # Optimize for speech recognition
        audio = audio.normalize()
        if audio.channels > 1:
            audio = audio.set_channels(1)
        if audio.frame_rate != 16000:
            audio = audio.set_frame_rate(16000)
        
        # Apply noise reduction
        audio = audio.high_pass_filter(80)
        
        # Export optimized audio
        audio.export(wav_file, format="wav")
        
        # Speech recognition
        with sr.AudioFile(wav_file) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
            
            try:
                text = recognizer.recognize_google(audio_data, language=src_lang)
                return text
            except sr.UnknownValueError:
                return f"Could not understand audio in {src_lang}"
            except sr.RequestError as e:
                return f"Speech recognition service error: {e}"
                
    except Exception as e:
        logger.error(f"Audio to text conversion failed: {e}")
        return f"Error processing audio: {str(e)}"
    
    finally:
        # Cleanup temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

def translate_text(text, src_lang="en", target_lang="hi"):
    """Enhanced text translation"""
    try:
        if not text or text.strip() == "":
            return "No text to translate"
        
        # Handle long text by splitting into chunks
        if len(text) > 5000:
            chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
            translated_chunks = []
            
            for chunk in chunks:
                translator = GoogleTranslator(source=src_lang, target=target_lang)
                translated_chunk = translator.translate(chunk)
                translated_chunks.append(translated_chunk)
            
            return ' '.join(translated_chunks)
        else:
            translator = GoogleTranslator(source=src_lang, target=target_lang)
            translated = translator.translate(text)
            return translated
            
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return f"Translation error: {str(e)}"

def text_to_speech(text, lang="hi", out_file="output.mp3", voice_type="standard"):
    """Enhanced text to speech with voice options"""
    try:
        if not text or text.strip() == "":
            raise ValueError("No text provided for TTS")
        
        # Handle text length limitations
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        # Configure TTS based on voice type
        slow_speech = voice_type == "slow"
        
        # Create TTS object
        tts = gTTS(text=text, lang=lang, slow=slow_speech)
        
        # Save to file
        tts.save(out_file)
        
        if os.path.exists(out_file):
            file_size = os.path.getsize(out_file)
            if file_size > 0:
                logger.info(f"TTS audio generated: {out_file} ({file_size} bytes)")
                
                # Post-process audio based on voice type
                if voice_type == "fast":
                    try:
                        audio = AudioSegment.from_file(out_file)
                        faster_audio = audio.speedup(playback_speed=1.25)
                        faster_audio.export(out_file, format="mp3")
                        logger.info("Applied fast speech processing")
                    except Exception as e:
                        logger.warning(f"Could not apply fast speech: {e}")
                
                return out_file
            else:
                raise FileNotFoundError("TTS file was created but is empty")
        else:
            raise FileNotFoundError("TTS file was not created")
            
    except Exception as e:
        logger.error(f"Text to speech conversion failed: {e}")
        raise e

def detect_language_from_audio(file_path, max_attempts=5):
    """Advanced language detection from audio"""
    common_languages = ['en-US', 'es-ES', 'fr-FR', 'de-DE', 'it-IT', 'pt-PT', 
                       'ru-RU', 'ja-JP', 'ko-KR', 'zh-CN', 'ar-SA', 'hi-IN']
    
    best_result = None
    best_confidence = 0.0
    detected_lang = 'en'
    
    for lang in common_languages[:max_attempts]:
        try:
            text_result = audio_to_text(file_path, src_lang=lang)
            if text_result and not text_result.startswith('Could not') and len(text_result.strip()) > 5:
                confidence = min(len(text_result.strip()) / 50.0, 1.0)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_result = text_result
                    detected_lang = lang.split('-')[0]
                    
                if confidence > 0.7:
                    break
                    
        except Exception as e:
            logger.debug(f"Language detection failed for {lang}: {e}")
            continue
    
    return detected_lang

def get_audio_info(file_path):
    """Get comprehensive audio file information"""
    try:
        audio = AudioSegment.from_file(file_path)
        return {
            'duration': len(audio) / 1000.0,
            'channels': audio.channels,
            'frame_rate': audio.frame_rate,
            'sample_width': audio.sample_width,
            'format': os.path.splitext(file_path)[1][1:].upper(),
            'file_size': os.path.getsize(file_path)
        }
    except Exception as e:
        logger.error(f"Error getting audio info: {e}")
        return None

def enhance_audio_quality(file_path, output_path=None):
    """Enhance audio quality for better voice output"""
    try:
        if output_path is None:
            output_path = f"enhanced_{os.path.basename(file_path)}"
        
        audio = AudioSegment.from_file(file_path)
        
        # Audio enhancements
        audio = audio.normalize()  # Normalize volume
        audio = audio.set_channels(1)  # Convert to mono for consistency
        
        # Apply gentle compression for better voice clarity
        audio = audio.compress_dynamic_range(threshold=-20.0, ratio=4.0, attack=5.0, release=50.0)
        
        # Export enhanced audio
        audio.export(output_path, format="mp3", bitrate="192k")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Audio enhancement failed: {e}")
        return file_path

if __name__ == "__main__":
    # Test the enhanced voice functions
    input_file = input("Enter full path to your audio file: ").strip('"')
    
    # Get audio info
    audio_info = get_audio_info(input_file)
    if audio_info:
        print(f"📊 Audio Info: {audio_info}")
    
    # Auto-detect language
    detect_lang = input("Auto-detect language? (y/n): ").lower() == 'y'
    
    if detect_lang:
        print("🔍 Detecting language...")
        source_lang = detect_language_from_audio(input_file)
        print(f"🌍 Detected language: {source_lang}")
    else:
        source_lang = input("Enter source language code: ")
    
    target_lang = input("Enter target language code: ")
    voice_type = input("Voice type (standard/slow/fast): ") or "standard"

    # Process with voice generation
    print("🎤 Converting speech to text...")
    sr_lang = f"{source_lang}-US" if '-' not in source_lang else source_lang
    text = audio_to_text(input_file, src_lang=sr_lang)
    print("📝 Text:", text)

    if source_lang != target_lang and not text.startswith('Could not'):
        print("🌐 Translating...")
        translated = translate_text(text, src_lang=source_lang, target_lang=target_lang)
        print(f"🔤 Translated Text: {translated}")
    else:
        translated = text

    if translated and not translated.startswith('Translation error'):
        print("🎵 Generating voice...")
        output = text_to_speech(translated, lang=target_lang, voice_type=voice_type)
        print(f"✅ Voice saved: {output}")
        
        # Get generated audio info
        voice_info = get_audio_info(output)
        if voice_info:
            print(f"🎵 Voice Info: Duration: {voice_info['duration']:.1f}s, Size: {voice_info['file_size']} bytes")
