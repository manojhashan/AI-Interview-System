from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from services.ai_service import generate_questions, analyze_answer

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return "Zynergy AI Backend is Running!"

@app.route('/api/generate-questions', methods=['POST'])
def generate_questions_route():
    try:
        data = request.json
        resume = data.get('resume')
        job_role = data.get('jobRole')

        if not resume or not job_role:
            return jsonify({"error": "Missing resume or jobRole"}), 400

        questions = generate_questions(resume, job_role)
        return jsonify(questions)
    except Exception as e:
        print(f"Error generating questions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-answer', methods=['POST'])
def analyze_answer_route():
    try:
        data = request.json
        question = data.get('question')
        answer = data.get('answer')
        audio_blob = data.get('audioBlob')
        image_frames = data.get('imageFrames')

        if not question or not answer:
            return jsonify({"error": "Missing question or answer"}), 400

        result = analyze_answer(question, answer, audio_blob, image_frames)
        return jsonify(result)
    except Exception as e:
        print(f"Error analyzing answer: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
