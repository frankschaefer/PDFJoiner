#!/bin/bash
# PDF Joiner - macOS/Linux Startup Script
# This script activates the virtual environment and starts the application

echo "===================================="
echo "PDF Batch Joiner v1.3.1"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "Virtual environment not found!"
    echo "Please run setup first:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
python -c "import customtkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Dependencies not installed!"
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies!"
        exit 1
    fi
fi

# Start the application
echo "Starting PDF Batch Joiner..."
echo ""
python main.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "Application exited with an error."
    read -p "Press Enter to continue..."
fi
