#!/bin/bash
# Setup script for HiveMind Architecture

set -e

echo "🐝 HiveMind Setup Script"
echo "======================="

# Check Python version
PYTHON_CMD=""
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
elif command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    if [[ $(echo "$PYTHON_VERSION >= 3.9" | bc -l) -eq 1 ]]; then
        PYTHON_CMD="python3"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Error: Python 3.9+ is required"
    exit 1
fi

echo "✓ Found $PYTHON_CMD"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
$PYTHON_CMD -m venv .venv
echo "✓ Virtual environment created"

# Activate and install dependencies
echo ""
echo "Installing dependencies..."
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "⚠  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "IMPORTANT: Edit .env and add your GOOGLE_API_KEY"
    echo ""
    echo "Get your API key from: https://makersuite.google.com/app/apikey"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo ""
    echo "✓ .env file already exists"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Setup complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "To activate the environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the system:"
echo "  python -m src.main"
echo ""
echo "Or run the example:"
echo "  python examples/example_execution.py"
echo ""
