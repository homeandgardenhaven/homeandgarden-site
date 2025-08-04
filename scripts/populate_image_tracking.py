#!/usr/bin/env python3
"""
Script to populate the used_images.json with existing images from markdown files
"""

import os
import re
import json
from pathlib import Path

def extract_images_from_markdown(file_path):
    """Extract image URLs from a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match markdown images: ![alt text](url)
    image_pattern = r'!\[.*?\]\((https://images\.unsplash\.com/photo-[^?)\s]+)'
    matches = re.findall(image_pattern, content)
    
    # Also check for hero images in frontmatter
    hero_pattern = r'hero:\s*["\']?(https://images\.unsplash\.com/photo-[^?"\'\s]+)'
    hero_matches = re.findall(hero_pattern, content)
    
    return matches + hero_matches

def populate_image_tracking():
    """Populate the used_images.json with existing images from all markdown files."""
    
    # Path to the content directory
    content_dir = Path("content/posts")
    used_images = {}
    
    if not content_dir.exists():
        print(f"Content directory {content_dir} not found")
        return
    
    # Process all markdown files
    for md_file in content_dir.glob("*.md"):
        page_name = md_file.stem  # filename without extension
        images = extract_images_from_markdown(md_file)
        
        print(f"\nProcessing {page_name}:")
        for image_url in images:
            base_url = image_url.split('?')[0]  # Remove URL parameters
            
            if base_url in used_images:
                print(f"  WARNING: Duplicate image found!")
                print(f"    Image: {base_url}")
                print(f"    Already used in: {used_images[base_url]}")
                print(f"    Also found in: {page_name}")
            else:
                used_images[base_url] = page_name
                print(f"  Added: {base_url}")
    
    # Save the results
    output_file = Path("scripts/used_images.json")
    with open(output_file, 'w') as f:
        json.dump(used_images, f, indent=4)
    
    print(f"\n✅ Saved {len(used_images)} unique images to {output_file}")
    
    # Summary statistics
    pages_with_images = len(set(used_images.values()))
    print(f"📊 Summary:")
    print(f"   Total unique images: {len(used_images)}")
    print(f"   Pages with images: {pages_with_images}")
    
    # Show pages and their image counts
    from collections import Counter
    page_counts = Counter(used_images.values())
    print(f"\n📄 Images per page:")
    for page, count in sorted(page_counts.items()):
        print(f"   {page}: {count} images")

if __name__ == "__main__":
    populate_image_tracking()
