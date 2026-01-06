#!/bin/bash

# Installation script for Python with Tkinter support on macOS
# This script reinstalls Python 3.12.1 with Tkinter support

set -e  # Exit on error

echo "=================================================="
echo "Python with Tkinter Installation Script"
echo "=================================================="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Error: Homebrew is not installed."
    echo "Please install Homebrew first: https://brew.sh"
    exit 1
fi

echo "Step 1/6: Installing compatible tcl-tk version (8.6)..."
# Uninstall newer version if present
brew uninstall --ignore-dependencies tcl-tk 2>/dev/null || true

# Install tcl-tk@8
brew install tcl-tk@8

echo ""
echo "Step 2/6: Setting up build environment..."
# For Apple Silicon Macs
if [[ $(uname -m) == 'arm64' ]]; then
    export LDFLAGS="-L/opt/homebrew/opt/tcl-tk@8/lib"
    export CPPFLAGS="-I/opt/homebrew/opt/tcl-tk@8/include"
    export PATH="/opt/homebrew/opt/tcl-tk@8/bin:$PATH"
    export PKG_CONFIG_PATH="/opt/homebrew/opt/tcl-tk@8/lib/pkgconfig"
    export PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I/opt/homebrew/opt/tcl-tk@8/include' --with-tcltk-libs='-L/opt/homebrew/opt/tcl-tk@8/lib -ltcl8.6 -ltk8.6'"
else
    # For Intel Macs
    export LDFLAGS="-L/usr/local/opt/tcl-tk@8/lib"
    export CPPFLAGS="-I/usr/local/opt/tcl-tk@8/include"
    export PATH="/usr/local/opt/tcl-tk@8/bin:$PATH"
    export PKG_CONFIG_PATH="/usr/local/opt/tcl-tk@8/lib/pkgconfig"
    export PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I/usr/local/opt/tcl-tk@8/include' --with-tcltk-libs='-L/usr/local/opt/tcl-tk@8/lib -ltcl8.6 -ltk8.6'"
fi

echo ""
echo "Step 3/6: Uninstalling Python 3.12.1 from pyenv..."
if pyenv versions | grep -q "3.12.1"; then
    pyenv uninstall -f 3.12.1
    echo "Python 3.12.1 uninstalled."
else
    echo "Python 3.12.1 not found in pyenv, skipping uninstall."
fi

echo ""
echo "Step 4/6: Installing Python 3.12.1 with Tkinter support..."
echo "This may take 5-10 minutes..."
pyenv install 3.12.1

echo ""
echo "Step 5/6: Verifying Tkinter installation..."
~/.pyenv/versions/3.12.1/bin/python3 -c "import tkinter; print('✓ Tkinter is working!')"

echo ""
echo "Step 6/6: Recreating virtual environment..."
cd "$(dirname "$0")"

# Deactivate if active
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate 2>/dev/null || true
fi

# Remove old venv
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi

# Create new venv
echo "Creating new virtual environment..."
~/.pyenv/versions/3.12.1/bin/python3 -m venv venv

# Activate venv
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=================================================="
echo "✓ Installation complete!"
echo "=================================================="
echo ""
echo "To start the application, run:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Or simply use the start script:"
echo "  ./start.sh"
echo ""
