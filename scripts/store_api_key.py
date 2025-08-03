#!/usr/bin/env python3
"""
Securely store API keys in macOS Keychain
"""

import keyring
import getpass
import sys

def store_unsplash_key():
    """Store Unsplash API key in keychain"""
    print("🔑 Securely storing your Unsplash API key in macOS Keychain")
    print()
    print("This will store your key encrypted in your user keychain,")
    print("which is much more secure than a plain text file.")
    print()
    
    # Get the API key securely
    api_key = getpass.getpass("Enter your Unsplash Access Key: ")
    
    if not api_key.strip():
        print("❌ No API key provided")
        return False
    
    try:
        # Store in keychain
        keyring.set_password("homeandgarden-website", "unsplash_api_key", api_key.strip())
        print("✅ API key stored securely in keychain")
        print()
        print("You can now run:")
        print("   python3 scripts/unsplash_manager.py")
        return True
        
    except Exception as e:
        print(f"❌ Error storing API key: {e}")
        return False

def verify_key():
    """Verify stored API key"""
    try:
        key = keyring.get_password("homeandgarden-website", "unsplash_api_key")
        if key:
            print(f"✅ API key found in keychain (starts with: {key[:8]}...)")
            return True
        else:
            print("❌ No API key found in keychain")
            return False
    except Exception as e:
        print(f"❌ Error accessing keychain: {e}")
        return False

def delete_key():
    """Delete stored API key"""
    try:
        keyring.delete_password("homeandgarden-website", "unsplash_api_key")
        print("✅ API key deleted from keychain")
        return True
    except Exception as e:
        print(f"❌ Error deleting key: {e}")
        return False

def main():
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        if action == "verify":
            verify_key()
        elif action == "delete":
            delete_key()
        else:
            print("Usage: python3 store_api_key.py [verify|delete]")
    else:
        store_unsplash_key()

if __name__ == "__main__":
    main()
