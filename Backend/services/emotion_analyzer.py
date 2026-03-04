"""
services/emotion_analyzer.py
-----------------------------
Facial Emotion + Head Pose Confidence Analyzer
================================================
- facial_emotion_model.h5  (trained model - 7 classes)
- OpenCV solvePnP           (head pose estimation - no mediapipe needed)
- Returns: confidence_score (0-100), dominant emotion, feedback string
"""

import os
import cv2
import numpy as np
import base64

# ─── Preload resources at module import (not lazily on first request) ────────
_emotion_model  = None
_face_cascade   = None
_eye_cascade    = None

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "trained_models", "facial_emotion_model.h5")

EMOTIONS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

# Scientific valence weights per emotion class index
# Angry=-0.6, Disgust=-0.8, Fear=-0.9, Happy=1.0, Neutral=0.8, Sad=-0.4, Surprise=0.2
VALENCE_WEIGHTS = {0: -0.6, 1: -0.8, 2: -0.9, 3: 1.0, 4: 0.8, 5: -0.4, 6: 0.2}


def _load_resources():
    """Load model + cascades once."""
    global _emotion_model, _face_cascade, _eye_cascade

    if _emotion_model is None:
        try:
            from tensorflow.keras.models import load_model
            _emotion_model = load_model(MODEL_PATH)
            print(f"[EmotionAnalyzer] Model loaded: {MODEL_PATH}")
        except Exception as e:
            print(f"[EmotionAnalyzer] ERROR loading model: {e}")
            _emotion_model = None

    if _face_cascade is None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _face_cascade = cv2.CascadeClassifier(cascade_path)

    if _eye_cascade is None:
        eye_path = cv2.data.haarcascades + "haarcascade_eye.xml"
        _eye_cascade = cv2.CascadeClassifier(eye_path)

# ── Preload immediately so first interview request is fast ─────────────────
try:
    _load_resources()
except Exception as _e:
    print(f"[EmotionAnalyzer] Preload failed (will retry on first request): {_e}")


# ─── Head Pose (Pure OpenCV solvePnP) ────────────────────────────────────────

# 3D reference points of a generic face model (in mm)
_FACE_3D_POINTS = np.array([
    [0.0,    0.0,    0.0],    # Nose tip
    [0.0,   -63.6, -12.5],   # Chin
    [-43.3,  32.7, -26.0],   # Left eye corner
    [43.3,   32.7, -26.0],   # Right eye corner
    [-28.9, -28.9, -24.1],   # Left mouth corner
    [28.9,  -28.9, -24.1],   # Right mouth corner
], dtype=np.float64)

def _get_head_pose(img_bgr: np.ndarray, face_rect: tuple):
    """
    Estimates head pitch & yaw from face bounding box + eye positions
    using OpenCV solvePnP. No mediapipe required.

    face_rect: (x, y, w, h) from Haar cascade
    Returns (pitch_deg, yaw_deg)
    """
    try:
        img_h, img_w = img_bgr.shape[:2]
        x, y, w, h = face_rect
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # Detect eyes inside face ROI
        face_roi = gray[y:y+h, x:x+w]
        eyes = _eye_cascade.detectMultiScale(face_roi, 1.1, 5)

        # Estimate 6 facial landmark positions from face bbox geometry
        fx = x + w // 2        # face X center
        fy = y + h // 2        # face Y center

        nose_2d    = [fx, fy]
        chin_2d    = [fx, y + h]
        ml_2d      = [x + w // 4,     y + int(h * 0.75)]
        mr_2d      = [x + 3 * w // 4, y + int(h * 0.75)]

        if len(eyes) >= 2:
            eyes_sorted = sorted(eyes, key=lambda e: e[0])
            le = eyes_sorted[0]; re = eyes_sorted[1]
            le_cx = x + le[0] + le[2] // 2;  le_cy = y + le[1] + le[3] // 2
            re_cx = x + re[0] + re[2] // 2;  re_cy = y + re[1] + re[3] // 2
        else:
            le_cx = x + w // 4;       le_cy = y + h // 3
            re_cx = x + 3 * w // 4;   re_cy = y + h // 3

        image_points = np.array([
            nose_2d, chin_2d,
            [le_cx, le_cy], [re_cx, re_cy],
            ml_2d, mr_2d
        ], dtype=np.float64)

        focal_length = img_w
        cam_matrix = np.array([
            [focal_length, 0,            img_w / 2],
            [0,            focal_length, img_h / 2],
            [0,            0,            1         ]
        ], dtype=np.float64)
        dist_coeffs = np.zeros((4, 1))

        success, rvec, tvec = cv2.solvePnP(
            _FACE_3D_POINTS, image_points, cam_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        if not success:
            return 0.0, 0.0

        rmat, _ = cv2.Rodrigues(rvec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
        pitch_deg = angles[0] * 360
        yaw_deg   = angles[1] * 360
        return float(pitch_deg), float(yaw_deg)

    except Exception as ex:
        print(f"[EmotionAnalyzer] Head pose error: {ex}")
        return 0.0, 0.0


# ─── Per-frame Analysis ───────────────────────────────────────────────────────

def _decode_frame(b64_image: str):
    """Decode a base64 data-URI image (from React webcam) into a numpy BGR array."""
    try:
        if "," in b64_image:
            _, encoded = b64_image.split(",", 1)
        else:
            encoded = b64_image
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"[EmotionAnalyzer] Frame decode error: {e}")
        return None


# ─── Public API ───────────────────────────────────────────────────────────────

# 27. Capture Facial Expressions
# Receives base64 image frames captured during the interview by the React frontend webcam
# 28. Analyze Facial Features — runs emotion model + head pose on each frame
# 29. Store Facial Analysis Results — returns dict stored in InterviewResult by main.py
def analyze_frames(frames: list) -> dict:
    """
    Analyze a list of base64 image frames captured during the interview answer.
    Uses a SINGLE batched TF prediction for all frames (much faster than per-frame predict).
    """
    _load_resources()  # no-op on subsequent calls

    if _emotion_model is None:
        return {
            "facial_score": 72.0,
            "dominant_emotion": "Neutral",
            "facial_feedback": "Facial model unavailable. Using default score.",
            "frames_analyzed": 0
        }

    if not frames:
        return {
            "facial_score": 70.0,
            "dominant_emotion": "Neutral",
            "facial_feedback": "No video frames received for analysis.",
            "frames_analyzed": 0
        }

    # 28. Analyze Facial Features — Step 1: Decode frames + Haar face detection
    rois           = []   # face crops (48×48 gray) for batch prediction
    imgs_with_faces = []

    for b64 in frames:
        img = _decode_frame(b64)
        if img is None:
            continue
        gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = _face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        if len(faces) == 0:
            continue
        x, y, w, h = faces[0]
        roi = cv2.resize(gray[y:y+h, x:x+w], (48, 48)).astype("float32") / 255.0
        roi = np.expand_dims(roi, axis=-1)   # (48, 48, 1)
        rois.append(roi)
        imgs_with_faces.append((img, (x, y, w, h)))

    if not rois:
        return {
            "facial_score": 65.0,
            "dominant_emotion": "Unknown",
            "facial_feedback": "No face detected in provided frames. Ensure good lighting and camera angle.",
            "frames_analyzed": 0
        }

    # 28. Analyze Facial Features — Step 2: Single batch CNN prediction (faster)
    batch = np.stack(rois, axis=0)          # (N, 48, 48, 1)
    predictions = _emotion_model.predict(batch, verbose=0)  # (N, 7)

    # 28. Analyze Facial Features — Step 3: Head pose + valence score per frame────
    results = []
    emotion_counts = {}
    pitch = 0.0

    for i, pred in enumerate(predictions):
        emotion_idx   = int(np.argmax(pred))
        raw_valence   = sum(float(pred[j]) * VALENCE_WEIGHTS[j] for j in range(7))
        emotion_score = ((raw_valence + 1) / 2) * 100

        # Head pose — only compute for first valid frame to save time
        if i == 0:
            img, face_rect = imgs_with_faces[i]
            pitch, _ = _get_head_pose(img, face_rect)

        pose_penalty = 30.0 if pitch < -10 else 0.0
        confidence   = max(0.0, min(100.0, emotion_score - pose_penalty))
        emotion_name = EMOTIONS[emotion_idx]

        results.append({"emotion": emotion_name, "confidence": round(confidence, 2)})
        emotion_counts[emotion_name] = emotion_counts.get(emotion_name, 0) + 1

    # ── Step 4: Aggregate ─────────────────────────────────────────────────────
    scores    = [r["confidence"] for r in results]
    avg_score = sum(scores) / len(scores)
    dominant  = max(emotion_counts, key=emotion_counts.get)

    std_dev = 0.0
    variance_penalty = 0.0
    if len(scores) > 1:
        variance         = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        std_dev          = variance ** 0.5
        variance_penalty = min(15.0, (std_dev / 30.0) * 15.0)

    dominant_ratio  = emotion_counts[dominant] / len(results)
    stability_bonus = dominant_ratio * 5.0
    final_score     = max(0.0, min(100.0, avg_score - variance_penalty + stability_bonus))
    final_score     = round(final_score, 2)

    # 29. Store Facial Analysis Results — aggregate and return
    return {
        "facial_score":      final_score,
        "dominant_emotion":  dominant,
        "facial_feedback":   _build_feedback(dominant, final_score, std_dev),
        "frames_analyzed":   len(results)
    }


def _build_feedback(emotion: str, score: float, std_dev: float = 0.0) -> str:
    """Generate a friendly feedback string based on dominant emotion, score, and stability."""
    if score >= 80:
        base = "Excellent facial confidence and engagement."
    elif score >= 60:
        base = "Good composure overall."
    else:
        base = "Try to maintain a more confident, open expression."

    if std_dev > 20:
        stability_msg = " Your expressions varied significantly — try to stay calm and consistent."
    elif std_dev > 10:
        stability_msg = " Some emotional fluctuation detected — a steadier expression will boost confidence."
    else:
        stability_msg = " Your expression was consistent and composed throughout."

    emotion_tips = {
        "Happy":    "Positive expressions like smiling build great rapport.",
        "Neutral":  "Steady and professional demeanor observed.",
        "Surprise": "Occasional surprise expressions noted — stay composed.",
        "Angry":    "Try to relax your facial muscles to appear more approachable.",
        "Fear":     "You appeared nervous in some frames. Deep breaths can help.",
        "Sad":      "Try to maintain an upbeat, enthusiastic expression.",
        "Disgust":  "Be mindful of expressions that may appear dismissive.",
    }
    tip = emotion_tips.get(emotion, "Keep practicing to improve your facial presence.")
    return f"{base}{stability_msg} {tip}"
