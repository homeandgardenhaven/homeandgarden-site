#!/usr/bin/env python3
"""
Quick script to get photo details for a specific Unsplash image
"""

import sys
import os
sys.path.append('scripts')

from unsplash_manager import ImageManager

def get_photo_info(photo_id):
    """Get photo information by ID"""
    try:
        manager = ImageManager()
        
        # Extract just the photo ID from the URL
        if 'photo-' in photo_id:
            photo_id = photo_id.replace('photo-', '')
        
        # Make direct API call to get photo details
        import requests
        url = f"https://api.unsplash.com/photos/{photo_id}"
        response = requests.get(url, headers=manager.headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Photographer: {data['user']['name']}")
            print(f"Username: @{data['user']['username']}")
            print(f"Photo URL: {data['links']['html']}")
            print(f"Alt description: {data.get('alt_description', 'No description')}")
            return data
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    photo_id = "1416879595969-9e5a4c8e8c8e"
    get_photo_info(photo_id)
