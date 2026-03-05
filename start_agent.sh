#!/bin/bash

echo "🤖 STARTING LEGAL AGENT SYSTEM"
echo "==============================="

# Kill any existing processes
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null
lsof -ti:3002 | xargs kill -9 2>/dev/null

# Start Python agent in background
echo "📡 Starting Python Agent on port 3002..."
cd backend
python agent_server.py &
PYTHON_PID=$!
cd ..

# Wait for Python agent to start
sleep 3

# Start Node server
echo "📡 Starting Node Server on port 3001..."
cd backend
node server.js &
NODE_PID=$!
cd ..

# Start frontend
echo "🌐 Starting Frontend on port 3000..."
cd frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ LEGAL AGENT SYSTEM RUNNING"
echo "==============================="
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Node Server: http://localhost:3001"
echo "🤖 Python Agent: http://localhost:3002"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
wait
