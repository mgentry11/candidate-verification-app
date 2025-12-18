#!/bin/bash

echo "🔍 Candidate Verification System - Simple Start"
echo ""

# Kill any existing processes on our ports
lsof -ti:5001 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Install dependencies
echo "📦 Installing dependencies..."
cd backend
source venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null || echo "Dependencies already installed"
cd ..

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.template .env
fi

echo ""
echo "🚀 Starting servers..."
echo ""

# Start backend on port 5001 (avoiding port 5000 conflict)
cd backend
source venv/bin/activate
FLASK_RUN_PORT=5001 python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend on port 8000
cd frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Application is running!"
echo ""
echo "   Backend:  http://localhost:5001"
echo "   Frontend: http://localhost:8000"
echo ""
echo "🌐 Open http://localhost:8000 in your browser"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Trap to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# Wait
wait
