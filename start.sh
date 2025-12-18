#!/bin/bash

# Candidate Verification System - Quick Start Script

echo "🔍 Candidate Verification System - Starting..."
echo ""

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment and install dependencies
echo "📦 Installing backend dependencies..."
cd backend
source venv/bin/activate

# Check if dependencies are installed
if ! pip show flask &> /dev/null; then
    pip install -r requirements.txt
fi

# Check if .env exists, if not create from template
if [ ! -f "../.env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp ../.env.template ../.env
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting backend server on http://localhost:5000"
echo "🌐 Starting frontend server on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the servers"
echo ""

# Start backend in background
python app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
cd ../frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!

echo ""
echo "✨ Application is running!"
echo "   Backend:  http://localhost:5000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Open http://localhost:3000 in your browser to use the application"
echo ""

# Wait for user to stop
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
