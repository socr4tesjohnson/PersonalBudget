#!/bin/bash

echo "=========================================="
echo "Personal Budget Planner - Web Server"
echo "=========================================="
echo ""

# Get the IP address
echo "Finding your server IP address..."
IP=$(hostname -I | awk '{print $1}')

if [ -z "$IP" ]; then
    echo "Could not automatically detect IP address."
    echo "Please check your network settings manually."
else
    echo "✓ Server IP: $IP"
fi

echo ""
echo "Starting web server..."
echo ""
echo "=========================================="
echo "ACCESS FROM YOUR PHONE:"
echo "=========================================="
echo ""
echo "1. Make sure your phone is on the SAME WiFi network"
echo ""
if [ -n "$IP" ]; then
    echo "2. Open your phone's browser and go to:"
    echo ""
    echo "   http://$IP:5000"
    echo ""
fi
echo "3. Start budgeting!"
echo ""
echo "=========================================="
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Start Flask app
python3 app.py
