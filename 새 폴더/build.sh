#!/bin/bash

echo "Building Game Text Translator..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not installed or not in PATH"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Using Python: $PYTHON_CMD"

# Install requirements
echo "Installing requirements..."
$PYTHON_CMD -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install requirements"
    exit 1
fi

# Build the C++ extension
echo "Building C++ extension..."
$PYTHON_CMD setup.py build_ext --inplace
if [ $? -ne 0 ]; then
    echo "Error: Failed to build C++ extension"
    echo "Falling back to Python-only mode..."
    echo
fi

echo
echo "Build complete!"
echo
echo "To run the program:"
echo "  $PYTHON_CMD game_translator.py"
echo
