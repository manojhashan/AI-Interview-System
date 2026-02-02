# Zynergy AI Interview System

An advanced AI-powered interview system designed to help candidates prepare for interviews by generating tailored questions and providing real-time analysis of their answers using audio and video feedback.

## 🚀 Features

- **Smart Question Generation**: Generates interview questions based on your specialized Resume and Job Role.
- **AI Answer Analysis**: Analyzes your video and audio response to provide comprehensive feedback.
- **Real-time Monitoring**: Uses camera and microphone to simulate a real interview environment.
- **Modern UI**: Built with a responsive and sleek interface for the best user experience.

## 🛠️ Tech Stack

### Frontend

- **React** (via Vite)
- **TypeScript**
- **Google GenAI SDK**

### Backend

- **Python**
- **Flask**
- **Google GenAI**

## 🏁 Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

- [Node.js](https://nodejs.org/) (Latest LTS recommended)
- [Python](https://www.python.org/) (3.8 or higher)
- Google Gemini API Key

### Installation

1.  **Clone the repository**

    ```bash
    git clone https://github.com/manojhashan/AI-Interview-System.git
    cd AI-Interview-System
    ```

2.  **Backend Setup**
    Navigate to the `Backend` directory and install dependencies.

    ```bash
    cd Backend
    python -m venv .venv
    .venv\Scripts\activate  # On Windows
    pip install -r requirements.txt
    ```

    _Note: Ensure you have a `.env` file in the Backend directory with your `GEMINI_API_KEY`._

3.  **Frontend Setup**
    Navigate to the `Frontend` directory and install dependencies.
    ```bash
    cd ../Frontend
    npm install
    ```

### Running the Application

You can easily start both the backend and frontend using the provided batch script:

1.  Go to the root directory.
2.  Double-click **`start_project.bat`**.

Or run them manually:

**Backend:**

```bash
cd Backend
python app.py
```

**Frontend:**

```bash
cd Frontend
npm run dev
```

- Frontend will run on: `http://localhost:3000` (or the port shown in terminal)
- Backend runs on: `http://localhost:5000`

## 👤 Author

**Manoj Hashan**

- GitHub: [@manojhashan](https://github.com/manojhashan)
- Project Repository: [AI-Interview-System](https://github.com/manojhashan/AI-Interview-System)

---

_Created for the Zynergy AI Interview System Project._
