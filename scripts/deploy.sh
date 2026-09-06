#!/bin/bash
set -e

echo "=== Short Drama Script Generator - Deploy ==="

cd "$(dirname "$0")/.."

echo "[1/3] Installing dependencies..."
pip install -r backend/requirements.txt

echo "[2/3] Creating data directories..."
mkdir -p backend/data/scripts backend/downloads

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "Created .env file. Please edit backend/.env to add your API Key."
fi

echo "[3/3] Starting server..."
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
