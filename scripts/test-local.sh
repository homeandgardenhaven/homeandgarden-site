#!/bin/bash

# Local Hugo Testing Script
# This builds and serves your site exactly as it will appear in production
# but with localhost URLs for proper local navigation

echo "🔨 Building site for local testing..."

# Function to find an available port
find_available_port() {
    local port=8080
    while lsof -i :$port >/dev/null 2>&1; do
        port=$((port + 1))
    done
    echo $port
}

# Kill any existing Python servers on common ports
pkill -f "python3 -m http.server" 2>/dev/null || true

# Find available port
PORT=$(find_available_port)
echo "📡 Using port $PORT"

# Clean and build with localhost baseURL
rm -rf public-local
hugo --gc --minify --baseURL "http://localhost:$PORT" --destination public-local

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "🚀 Starting local server at http://localhost:$PORT"
    echo "📝 This matches your production build but with localhost navigation"
    echo "🛑 Press Ctrl+C to stop the server"
    echo ""
    
    # Start server
    cd public-local
    python3 -m http.server $PORT
else
    echo "❌ Build failed!"
    exit 1
fi
