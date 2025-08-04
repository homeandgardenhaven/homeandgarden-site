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
import logging

class ImageManager:
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
        self.used_images_file = Path("scripts/used_images.json")
        self.used_images = self._load_used_images()  # Track used image URLs
    
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
    
    def score_image_relevance(self, photo_data, search_term):
        """Score image relevance based on description and tags."""
        description = photo_data.get('alt_description', '').lower()
        tags = [tag['title'].lower() for tag in photo_data.get('tags', [])]
        score = 0
        if search_term.lower() in description:
            score += 2
        if any(search_term.lower() in tag for tag in tags):
            score += 1
        return score

    def is_image_high_quality(self, photo_data):
        """Check if the image meets quality and style guidelines."""
        width = photo_data['width']
        height = photo_data['height']
        aspect_ratio = width / height
        return width >= 1200 and 1.3 <= aspect_ratio <= 1.8  # Example landscape ratio

    def _load_used_images(self):
        """Load the mapping of images to pages from a JSON file."""
        if self.used_images_file.exists():
            with open(self.used_images_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_used_images(self):
        """Save the updated mapping of images to pages to the JSON file."""
        with open(self.used_images_file, 'w') as f:
            json.dump(self.used_images, f, indent=4)

    def is_image_unique(self, photo_data, page_name=None):
        """Check if the image is unique within the article and across articles."""
        image_url = photo_data['urls']['regular']
        # Extract base URL without parameters for duplicate checking
        base_url = image_url.split('?')[0]
        
        # Check if image is already used on any page
        if base_url in self.used_images:
            existing_page = self.used_images[base_url]
            print(f"Warning: Image {base_url} is already used on page: {existing_page}")
            return False
        
        # Check if the current page already has this image (within-page duplicate)
        if page_name:
            for existing_url, existing_page in self.used_images.items():
                if existing_page == page_name and existing_url == base_url:
                    print(f"Warning: Image {base_url} is already used on the same page: {page_name}")
                    return False
        
        # Only add to tracking if page_name is provided
        if page_name:
            self.used_images[base_url] = page_name
            self._save_used_images()
        
        return True

    def check_page_image_duplicates(self, page_name):
        """Check for duplicate images within a specific page."""
        page_images = [url for url, page in self.used_images.items() if page == page_name]
        duplicates = []
        seen = set()
        
        for image_url in page_images:
            if image_url in seen:
                duplicates.append(image_url)
            else:
                seen.add(image_url)
        
        return duplicates

    def get_images_for_page(self, page_name):
        """Get all images used on a specific page."""
        return [url for url, page in self.used_images.items() if page == page_name]

    def remove_image_from_tracking(self, image_url, page_name=None):
        """Remove an image from tracking."""
        base_url = image_url.split('?')[0]
        if base_url in self.used_images:
            if page_name is None or self.used_images[base_url] == page_name:
                del self.used_images[base_url]
                self._save_used_images()
                return True
        return False

    def log_image_selection(self, photo_data, reason):
        """Log the image selection process."""
        logging.info(f"Image URL: {photo_data['urls']['regular']}, Reason: {reason}")

    def select_best_image(self, search_results, search_term):
        """Select the best image based on relevance, quality, and uniqueness."""
        best_image = None
        highest_score = 0
        for photo in search_results['results']:
            if not self.is_image_high_quality(photo) or not self.is_image_unique(photo):
                self.log_image_selection(photo, "Rejected: Low quality or duplicate")
                continue
            relevance_score = self.score_image_relevance(photo, search_term)
            if relevance_score > highest_score:
                best_image = photo
                highest_score = relevance_score
        if best_image:
            self.log_image_selection(best_image, "Selected: Best match")
        return best_image

    def get_photo_for_post_with_review(self, search_term, alt_text=None, width=1200):
        """Get image markdown with automated and manual review."""
        try:
            results = self.search_photos(search_term)
            best_image = self.select_best_image(results, search_term)
            if best_image:
                return self.get_hotlink_markdown(best_image, alt_text, width)
            else:
                print(f"No suitable image found for '{search_term}'. Please review manually.")
                for photo in results['results']:
                    print(f"Image: {photo['urls']['regular']}")
                    print(f"Description: {photo['alt_description']}")
                return None
        except Exception as e:
            print(f"Error fetching photo: {e}")
            return None

def main():
    """Example usage"""
    # Initialize with config file
    try:
        manager = ImageManager()
    except Exception as e:
        print(f"Error loading config: {e}")
        print("Run 'uv run store_api_key.py' to securely store your API key")
        return

    # Example searches for garden content
    searches = [
        ("vegetable garden raised beds", "Raised vegetable beds with lush summer crops"),
        ("watering can garden summer", "Watering can in a sunlit garden"),
        ("ladybug green leaf macro", "Ladybug on a green leaf"),
        ("green lawn sprinkler summer", "Green lawn with sprinkler in summer sun"),
        ("garden pergola shade plants", "Pergola with climbing plants providing shade")
    ]
    print("Generating image markdown for garden content...")
    for search_term, alt_text in searches:
        markdown = manager.get_photo_for_post_with_review(search_term, alt_text=alt_text)
        if markdown:
            print(markdown)
        print()

if __name__ == "__main__":
    main()
