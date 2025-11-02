#!/bin/bash
# Install Python dependencies for jsk_enshu_recognition package
# This script installs packages to the user's local Python environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_DIR="$(dirname "$SCRIPT_DIR")"

echo "Installing Python dependencies for jsk_enshu_recognition..."
echo "Installation will be done in user space (~/.local/lib/python3.x/site-packages)"

# Install dependencies using pip with --user flag (user installation)
pip3 install --user -r "${PACKAGE_DIR}/requirements.txt"

echo ""
echo "✓ Dependencies installed successfully!"
echo ""
echo "Note: If this is the first time installing packages with --user,"
echo "you may need to add ~/.local/bin to your PATH:"
echo "  export PATH=\$HOME/.local/bin:\$PATH"
echo ""
echo "You can verify the installation by running:"
echo "  python3 -c 'import mediapipe; import tensorflow; print(\"OK\")'"
