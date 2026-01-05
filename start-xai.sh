#!/bin/bash

# EduMind XAI Integration Test Script

echo "🚀 Starting EduMind XAI Integration..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Start Backend
echo -e "${YELLOW}Step 1: Starting XAI Backend Service...${NC}"
cd backend/services/service-xai-prediction

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

# Start backend in background
echo "Starting FastAPI server on port 8000..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Starting Frontend...${NC}"
cd ../../../apps/web

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    pnpm install
fi

# Start frontend
echo "Starting Vite dev server..."
pnpm dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✅ Integration Complete!${NC}"
echo ""
echo "Backend API:  http://localhost:8000"
echo "API Docs:     http://localhost:8000/api/v1/docs"
echo "Frontend:     http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for user interrupt
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
