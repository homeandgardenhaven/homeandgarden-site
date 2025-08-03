#!/bin/bash
# Setup script for Unsplash API integration using uv and secure storage

echo "🌱 Setting up Unsplash API integration for Home and Garden Haven"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is required but not installed"
  #  echo "📦 Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
  #  echo "   or: brew install uv"
    exit 1
fi

# Create virtual environment and install dependencies
echo "📦 Creating virtual environment with uv..."
cd scripts
uv venv
echo "✅ Virtual environment created"

echo "📦 Installing dependencies..."
uv add requests Pillow PyYAML keyring
echo "✅ Dependencies installed"

# Check if we're on macOS (keychain support)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "🔑 SECURE API KEY STORAGE (macOS Keychain)"
    echo "   Your API key will be encrypted and stored in your user keychain"
    echo "   This is much more secure than plain text files"
    echo ""
    echo "🔑 To store your Unsplash Access Key securely:"
    echo "   uv run store_api_key.py"
    echo ""
    echo "   Your Unsplash keys (use Access Key only):"
    echo "   - Application ID: Not needed for basic API calls"
    echo "   - Access Key: ✅ Use this one"
    echo "   - Secret Key: Only needed for OAuth (not required)"
    echo ""
    echo "🚀 After storing your key, test with:"
    echo "   uv run unsplash_manager.py"
else
    echo ""
    echo "🔑 NON-MACOS SYSTEM DETECTED"
    echo "   Keychain storage not available"
    echo "   Using environment variable fallback"
    echo ""
    echo "   Set your API key:"
    echo "   export UNSPLASH_ACCESS_KEY='your_access_key_here'"
    echo ""
    echo "🚀 Test with:"
    echo "   uv run unsplash_manager.py"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "💡 Useful commands:"
echo "   uv run store_api_key.py verify  # Check if key is stored"
echo "   uv run store_api_key.py delete  # Remove stored key"
echo "   uv run unsplash_manager.py      # Download sample images"
