@echo off
echo Starting Zynergy AI Interview System...

:: Start Backend in a new window
start "Zynergy Backend" cmd /k "cd Backend && python app.py"

:: Start Frontend in a new window
start "Zynergy Frontend" cmd /k "cd Frontend && npm run dev"

echo Both services are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
pause

