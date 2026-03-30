#!/bin/bash

# ==========================================
# Arlo Camera System - Quick Start Script
# For macOS and Linux
# ==========================================

echo "🎥 Arlo Camera Management System - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "✓ Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is not installed!"
    echo "  Install from: https://www.python.org/downloads/"
    exit 1
fi
python_version=$(python3 --version)
echo "  Found: $python_version"

# Check Node.js version
echo "✓ Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "✗ Node.js is not installed!"
    echo "  Install from: https://nodejs.org/"
    exit 1
fi
node_version=$(node --version)
echo "  Found: Node.js $node_version"

echo ""
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Checking for .env file..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✓ Created .env file from template"
        echo "  ⚠️  Edit .env with your credentials before running!"
    else
        echo "✗ .env.example not found!"
        exit 1
    fi
else
    echo "✓ .env file already exists"
fi

echo ""
echo "Installing Node.js dependencies..."
npm install

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials:"
echo "   nano .env"
echo ""
echo "2. Start the backend server (Terminal 1):"
echo "   source venv/bin/activate"
echo "   python arlo_backend.py"
echo ""
echo "3. Start the frontend (Terminal 2):"
echo "   npm start"
echo ""
echo "4. Open dashboard: http://localhost:3000"
echo ""
echo "For detailed setup: cat SETUP_GUIDE.md"
