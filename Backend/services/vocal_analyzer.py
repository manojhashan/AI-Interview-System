"""
services/vocal_analyzer.py
-----------------------------
Vocal Confidence Analyzer
================================================
- vocal_model.h5 (trained model - 2 classes: e.g. 0=Not Confident, 1=Confident)
- Input: (1, 64, 128, 1) Mel-spectrogram
- Returns: confidence_score (0-100), feedback string
"""

import os
import base64
import tempfile
import numpy as np
import traceback

_vocal_model = None

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "trained_models", "vocal_model.h5")

def _load_resources():
    global _vocal_model
    if _vocal_model is None:
        try:
            from tensorflow.keras.models import load_model
            _vocal_model = load_model(MODEL_PATH)
            print(f"[VocalAnalyzer] Model loaded: {MODEL_PATH}")
        except Exception as e:
            print(f"[VocalAnalyzer] ERROR loading model: {e}")
            _vocal_model = None

try:
    _load_resources()
except Exception as _e:
    print(f"[VocalAnalyzer] Preload failed (will retry on first request): {_e}")


# 24. Capture Audio Input
# Decode base64 WAV audio sent from the frontend recorder
def _decode_audio(b64_audio: str) -> str:
    """Decodes base64 audio and saves to a temporary WAV file, returns the file path."""
    try:
        if "," in b64_audio:
            _, encoded = b64_audio.split(",", 1)
        else:
            encoded = b64_audio
        audio_bytes = base64.b64decode(encoded)
        
        # Always save as .wav (frontend converts to WAV before sending)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.write(audio_bytes)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        print(f"[VocalAnalyzer] Audio decode error: {e}")
        return None

# 24. Analyze Vocal Features — pitch, energy, speech rate via Mel-spectrogram + CNN model
# 25. Generate Vocal Feedback — returns score + human-readable feedback
# 26. Store Vocal Analysis Results — returned dict stored in InterviewResult by main.py
def analyze_audio(b64_audio: str) -> dict:
    import librosa
    
    _load_resources()
    
    if _vocal_model is None:
        return {
            "vocal_score": 75.0,
            "vocal_feedback": "Vocal model unavailable. Using default score."
        }
        
    if not b64_audio:
        return {
            "vocal_score": 0.0,
            "vocal_feedback": "No speech detected. Please speak clearly when answering."
        }
        
    temp_path = _decode_audio(b64_audio)
    if not temp_path:
        return {
            "vocal_score": 65.0,
            "vocal_feedback": "Failed to decode audio."
        }
        
    try:
        # Load audio (assuming native sample rate or 22050 librosa default)
        y, sr = librosa.load(temp_path, sr=22050)
        
        # Check if audio is completely silent or just background noise
        if len(y) == 0 or np.max(np.abs(y)) < 0.02:
            return {
                "vocal_score": 0.0,
                "vocal_feedback": "Audio is too quiet or silent. Please check your microphone."
            }
        
        # Extract mel-spectrogram with 64 mels
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

        # Normalize same as training preprocessing 
        mel_spec_db = (mel_spec_db - np.mean(mel_spec_db)) / (np.std(mel_spec_db) + 1e-6)
        
        # Shape fixing to exactly 128 frames
        max_len = 128
        if mel_spec_db.shape[1] < max_len:
            pad_width = max_len - mel_spec_db.shape[1]
            mel_spec_db = np.pad(mel_spec_db, pad_width=((0, 0), (0, pad_width)), mode='constant')
        else:
            mel_spec_db = mel_spec_db[:, :max_len]
            
        # Reshape for model input (1, 64, 128, 1)
        features = mel_spec_db.reshape(1, 64, 128, 1)
        
        # 24. Analyze Vocal Features
        # Mel-spectrogram fed to CNN model → confident (1) / not confident (0)
        predictions = _vocal_model.predict(features, verbose=0)[0]
        
        # Class index 1 = Confident — score scaled to 0–100
        vocal_score = float(predictions[1]) * 100
        
        if vocal_score >= 80:
            feedback = "Excellent vocal clarity, tone, and pacing. Very confident."
        elif vocal_score >= 60:
            feedback = "Good vocal delivery, with minor areas for improvement in pacing or tone."
        else:
            feedback = "Try to speak more clearly and steadily to improve vocal confidence."
            
        # 26. Store Vocal Analysis Results
        return {
            "vocal_score": round(max(0.0, min(100.0, vocal_score)), 2),
            "vocal_feedback": feedback
        }
    except Exception as e:
        print(f"[VocalAnalyzer] Analysis error: {e}")
        traceback.print_exc()
        return {
            "vocal_score": 70.0,
            "vocal_feedback": "Audio analysis failed due to an error."
        }
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"[VocalAnalyzer] Failed to remove temp audio file: {e}")
