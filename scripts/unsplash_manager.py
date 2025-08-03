#!/usr/bin/env python3
"""
Unsplash API Integration for Home and Garden Haven
Automatically downloads and optimizes images for blog posts
"""

import os
import requests
import json
from pathlib import Path
from PIL import Image
import yaml
import keyring

class UnsplashImageManager:
    def __init__(self, api_key=None, config_file=None):
        if config_file:
            self.load_config(config_file)
        else:
            self.api_key = api_key or self._get_api_key()
        
        if not self.api_key:
            raise ValueError(
                "Unsplash API key is required. "
                "Run 'python3 scripts/store_api_key.py' to securely store your key"
            )
        
        self.base_url = "https://api.unsplash.com"
        self.headers = {
            "Authorization": f"Client-ID {self.api_key}",
            "Accept-Version": "v1"
        }
    
    def _get_api_key(self):
        """Get API key from secure storage (keychain) or environment"""
        # Try keychain first (most secure)
        try:
            key = keyring.get_password("homeandgarden-website", "unsplash_api_key")
            if key:
                return key
        except Exception as e:
            print(f"Warning: Could not access keychain: {e}")
        
        # Fallback to environment variable
        return os.getenv('UNSPLASH_ACCESS_KEY')
    
    def load_config(self, config_file):
        """Load configuration from YAML file"""
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Handle environment variable references
        api_key_config = config['content']['images']['image_api']['keys']['unsplash']
        if api_key_config.startswith('env:'):
            env_var = api_key_config.replace('env:', '')
            self.api_key = os.getenv(env_var)
        else:
            self.api_key = api_key_config
            
        self.max_width = config['content']['images']['optimization']['max_width']
        self.compress = config['content']['images']['optimization']['compress']
    
    def search_photos(self, query, per_page=1, orientation="landscape"):
        """Search for photos on Unsplash"""
        url = f"{self.base_url}/search/photos"
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": orientation
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_hotlink_markdown(self, photo_data, alt_text=None, width=1200):
        """Return markdown for Unsplash hotlink with attribution"""
        image_url = photo_data['urls']['regular']
        if width:
            # Add width param to Unsplash URL for optimization
            if '?' in image_url:
                image_url += f'&w={width}'
            else:
                image_url += f'?w={width}'
        alt = alt_text or photo_data['alt_description'] or 'Unsplash photo'
        photographer = photo_data['user']['name']
        photographer_url = photo_data['user']['links']['html']
        photo_url = photo_data['links']['html']
        # Markdown image with attribution below
        markdown = f"![{alt}]({image_url})\n\n<sub>Photo by [" + photographer + f"]({photographer_url}) on [Unsplash]({photo_url})</sub>"
        return markdown
    
    def optimize_image(self, image_path):
        """Optimize image size and quality"""
        with Image.open(image_path) as img:
            # Resize if too wide
            if img.width > self.max_width:
                ratio = self.max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((self.max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save with optimization
            img.save(image_path, optimize=True, quality=85)
    
    def get_photo_for_post(self, search_term, alt_text=None, width=1200):
        """Get Unsplash hotlink markdown and attribution for a blog post"""
        try:
            results = self.search_photos(search_term)
            if results['results']:
                photo = results['results'][0]
                markdown = self.get_hotlink_markdown(photo, alt_text=alt_text, width=width)
                print(f"✅ Markdown for '{search_term}':\n{markdown}\n")
                return markdown
            else:
                print(f"❌ No photos found for: {search_term}")
                return None
        except Exception as e:
            print(f"❌ Error fetching photo: {e}")
            return None

def main():
    """Example usage"""
    # Initialize with config file
    try:
        manager = UnsplashImageManager()
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        print("💡 Run 'uv run store_api_key.py' to securely store your API key")
        return
    
    # Example searches for garden content
    searches = [
        ("vegetable garden raised beds", "Raised vegetable beds with lush summer crops"),
        ("watering can garden summer", "Watering can in a sunlit garden"),
        ("ladybug green leaf macro", "Ladybug on a green leaf"),
        ("green lawn sprinkler summer", "Green lawn with sprinkler in summer sun"),
        ("garden pergola shade plants", "Pergola with climbing plants providing shade")
    ]
    print("🌱 Generating Unsplash hotlink markdown for garden images...")
    for search_term, alt_text in searches:
        manager.get_photo_for_post(search_term, alt_text=alt_text)
        print()

if __name__ == "__main__":
    main()
