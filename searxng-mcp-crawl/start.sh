#!/bin/bash
# SearXNG MCP Server - Simple Startup Script
# Double-click this file to start the server!

echo "🚀 Starting SearXNG MCP Server..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo ""
    echo "Please install Node.js from: https://nodejs.org"
    echo "Press Enter to exit..."
    read
    exit 1
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if .env file exists, if not create it with defaults
if [ ! -f ".env" ]; then
    echo "📝 Creating default configuration..."
    cat > .env << EOF
# SearXNG MCP Server Configuration
SEARXNG_BASE_URL=http://localhost:32768
HOST=127.0.0.1
PORT=32769
DESIRED_TIMEZONE=UTC
CONTENT_MAX_LENGTH=10000
SEARCH_RESULT_LIMIT=10
EOF
    echo "✅ Configuration file created: .env"
    echo ""
fi

# Source the .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "📋 Configuration:"
echo "   SearXNG URL: $SEARXNG_BASE_URL"
echo "   Server will run at: http://$HOST:$PORT"
echo ""

# Start the server
echo "🔄 Starting server..."
npx .

# Keep terminal open on error
if [ $? -ne 0 ]; then
    echo ""
    echo "Press Enter to exit..."
    read
fi
