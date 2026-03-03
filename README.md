# Zynergy AI Interview System

An advanced AI-powered interview system that evaluates candidates using multimodal analysis — facial expressions, vocal tone, and semantic understanding — powered by Google Gemini.

## 🚀 Features

- **Smart Question Generation** — AI-generated questions tailored to your resume and job role
- **Multimodal Analysis** — Real-time facial emotion, vocal confidence & semantic answer scoring
- **Explainable AI (XAI)** — SHAP-based transparent feedback per modality
- **Admin Dashboard** — View all candidate results with detailed reports
- **Email OTP** — Secure password recovery via email verification
- **Modern UI** — Responsive dark-mode interface built with React + TypeScript

## 🛠️ Tech Stack

### Frontend

- **React** + **TypeScript** (via Vite)
- **Google Gemini API** (question generation & answer feedback)

### Backend

- **Python** + **FastAPI**
- **SQLAlchemy** + **PostgreSQL**
- **TensorFlow / Keras** (facial emotion model)
- **OpenCV** (head pose estimation)
- **Google Gemini API** (semantic feedback & summaries)

---

## 📥 Download & Setup

> ⚠️ **This is a research project.** The source code is available for **reference and learning only**.  
> Contributions and modifications to this repository are not accepted.

### Download

**[⬇️ Download ZIP](https://github.com/manojhashan/AI-Interview-System/archive/refs/heads/main.zip)**

Extract the ZIP and follow the steps below.

---

### Prerequisites

- [Node.js](https://nodejs.org/) (Latest LTS)
- [Python](https://www.python.org/) 3.8 or higher
- A **Google Gemini API Key** — [Get one here](https://aistudio.google.com/app/apikey)
- A **Gmail App Password** — for OTP email delivery

---

### Backend Setup

```bash
cd Backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file inside the `Backend` folder:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=your_postgresql_connection_string
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_APP_PASSWORD=your_gmail_app_password
```

> **Note:** Never share your `.env` file. Each user must create their own with their own API keys.

Start the backend:

```bash
python main.py
```

Backend runs on: `http://localhost:5000`

---

### Frontend Setup

```bash
cd Frontend
npm install
npm run dev
```

Frontend runs on: `http://localhost:5173`

---

## 👤 Author

**Manoj Hashan**

- GitHub: [@manojhashan](https://github.com/manojhashan)
- Project: [AI-Interview-System](https://github.com/manojhashan/AI-Interview-System)

---

_Zynergy AI Interview System — Research Project, 2025_
