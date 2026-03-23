import speech_recognition as sr
import base64
import tempfile
import os

def transcribe_base64_audio(b64_audio: str, language: str = "en-US") -> str:
    """
    Decodes a base64 string to a temporary WAV file and transcribes it using Google Web Speech API.
    Returns the transcribed text or an empty string if it fails.
    """
    if not b64_audio:
        return ""

    temp_path = None
    try:
        if "," in b64_audio:
            _, encoded = b64_audio.split(",", 1)
        else:
            encoded = b64_audio
            
        audio_bytes = base64.b64decode(encoded)
        
        # Save to a temporary WAV file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.write(audio_bytes)
        temp_file.close()
        temp_path = temp_file.name

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=language)
            return text
            
    except sr.UnknownValueError:
        print("[SpeechToText] Google Web Speech API could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"[SpeechToText] Could not request results from Google Web Speech API: {e}")
        return ""
    except Exception as e:
        print(f"[SpeechToText] Transcription error: {e}")
        return ""
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"[SpeechToText] Failed to remove temp audio file: {e}")
