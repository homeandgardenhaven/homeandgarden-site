#!/usr/bin/env python3
"""
Create a favicon from an Unsplash image
Downloads an image and converts it to proper favicon formats
"""

import requests
from PIL import Image, ImageFilter, ImageEnhance
import io
import os

def download_and_create_favicon(image_url, output_path="../static"):
    """Download image and create favicon in multiple sizes"""
    
    # Download the image
    print(f"Downloading image from: {image_url}")
    response = requests.get(image_url)
    response.raise_for_status()
    
    # Open the image
    img = Image.open(io.BytesIO(response.content))
    
    # Convert to RGBA if needed
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Create a square crop (centered)
    width, height = img.size
    size = min(width, height)
    
    # Calculate crop box for center crop
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top + size
    
    img_cropped = img.crop((left, top, right, bottom))
    
    # Enhance the image for favicon
    enhancer = ImageEnhance.Contrast(img_cropped)
    img_enhanced = enhancer.enhance(1.2)  # Increase contrast slightly
    
    # Create different sizes
    sizes = [16, 32, 48, 64, 128, 256]
    
    for size in sizes:
        # Resize with high quality
        resized = img_enhanced.resize((size, size), Image.Resampling.LANCZOS)
        
        # Save as PNG for modern browsers
        png_path = f"{output_path}/favicon-{size}x{size}.png"
        resized.save(png_path, "PNG", optimize=True)
        print(f"Created: {png_path}")
    
    # Create the main favicon.ico (16x16 and 32x32)
    favicon_sizes = [16, 32]
    favicon_images = []
    
    for size in favicon_sizes:
        resized = img_enhanced.resize((size, size), Image.Resampling.LANCZOS)
        # Convert to RGB for ICO format
        if resized.mode == 'RGBA':
            # Create white background for transparency
            background = Image.new('RGB', resized.size, (255, 255, 255))
            background.paste(resized, mask=resized.split()[-1])  # Use alpha as mask
            resized = background
        favicon_images.append(resized)
    
    # Save as favicon.ico
    favicon_path = f"{output_path}/favicon.ico"
    favicon_images[0].save(
        favicon_path,
        format='ICO',
        sizes=[(16, 16), (32, 32)]
    )
    print(f"Created: {favicon_path}")
    
    # Create apple-touch-icon
    apple_icon = img_enhanced.resize((180, 180), Image.Resampling.LANCZOS)
    apple_path = f"{output_path}/apple-touch-icon.png"
    apple_icon.save(apple_path, "PNG", optimize=True)
    print(f"Created: {apple_path}")
    
    print(f"\n✅ Favicon creation complete!")
    print(f"Files created in: {output_path}")

if __name__ == "__main__":
    # Use the nice potted plant image
    image_url = "https://images.unsplash.com/photo-1572688484438-313a6e50c333?w=400"
    download_and_create_favicon(image_url)
