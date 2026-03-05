#!/bin/bash

# Start Ollama service
echo "🚀 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to start
sleep 5

# Start FastAPI backend
echo "🚀 Starting FastAPI backend..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Open browser
echo "📂 Opening application in browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    open ../frontend/index.html
else
    xdg-open ../frontend/index.html
fi

echo ""
echo "✅ All services started!"
echo "📝 Press Ctrl+C to stop all services"

# Wait for user interrupt
wait $BACKEND_PID
