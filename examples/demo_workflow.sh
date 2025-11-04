#!/bin/bash
# Demo workflow script for ZETA CLI
# This demonstrates a typical ZETA usage session

echo "=== ZETA CLI Demo Workflow ==="
echo ""

echo "1. Creating a simple Python script..."
zeta run "create a Python script that prints 'Hello, ZETA!'"

echo ""
echo "2. Creating a webpage with teaching mode..."
zeta run "create an HTML page with a heading and a button" --teach

echo ""
echo "3. Reviewing code with critic mode..."
zeta run "review my Python files" --critic

echo ""
echo "4. Viewing learning log..."
zeta log

echo ""
echo "=== Demo Complete ==="

