#!/bin/bash

echo "========================================"
echo "  PlantGuard AI - Starting Server"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

echo
echo "Checking model files..."
if [ ! -d "agri-plant-disease-resnet50" ]; then
    echo "ERROR: Model directory not found!"
    echo "Please run: git clone https://huggingface.co/mesabo/agri-plant-disease-resnet50"
    exit 1
fi

echo
echo "========================================"
echo "  Server will start on: http://localhost:5000"
echo "========================================"
echo
echo "Tips:"
echo "  - Upload clear photos of plant leaves"
echo "  - Ask questions about plant diseases"
echo "  - Press Ctrl+C to stop the server"
echo
echo "========================================"
echo

python app.py
