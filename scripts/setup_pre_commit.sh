#!/bin/bash
# Setup script for pre-commit hooks

echo "Setting up pre-commit hooks..."

# Install pre-commit if not already installed
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip install pre-commit
fi

# Install hooks
pre-commit install

echo ""
echo "Pre-commit hooks installed successfully!"
echo ""
echo "Hooks will run automatically on git commit."
echo "To run manually: pre-commit run --all-files"

