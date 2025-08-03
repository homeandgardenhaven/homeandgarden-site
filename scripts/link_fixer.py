#!/usr/bin/env python3
"""
Link Fixer - Automatically fix broken links in markdown files
Usage: python link_fixer.py <markdown_file_path>
"""

import requests
import sys
import re
import os

def test_url(url, timeout=5):
    """Test if a URL is working"""
    try:
        response = requests.head(url, allow_redirects=True, timeout=timeout)
        return response.status_code < 400
    except:
        try:
            response = requests.get(url, allow_redirects=True, timeout=timeout)
            return response.status_code < 400
        except:
            return False

def find_wikipedia_alternatives(topic):
    """Find working Wikipedia alternatives for a topic"""
    base_patterns = [
        f"https://en.wikipedia.org/wiki/{topic}",
        f"https://en.wikipedia.org/wiki/{topic.replace('_', '-')}",
        f"https://en.wikipedia.org/wiki/{topic.replace('-', '_')}",
        f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
        f"https://simple.wikipedia.org/wiki/{topic}",
    ]
    
    # Try common topic variations
    variations = [
        topic,
        topic.replace('gardening', 'garden'),
        topic.replace('garden', 'gardening'),
        topic.capitalize(),
        topic.title(),
    ]
    
    all_patterns = []
    for variation in variations:
        for pattern in base_patterns:
            url = pattern.format(topic=variation)
            if url not in all_patterns:
                all_patterns.append(url)
    
    for url in all_patterns:
        print(f"  Testing: {url}")
        if test_url(url):
            return url
    
    return None

def fix_links_in_file(file_path):
    """Fix broken links in a markdown file"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # Find all markdown links [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = re.findall(link_pattern, content)
    
    print(f"🔍 Found {len(links)} links to check in {os.path.basename(file_path)}")
    
    for text, url in links:
        print(f"\n🔗 Checking: {text} -> {url}")
        
        if url.startswith('#') or url.startswith('/') or url.startswith('{{'):
            print(f"  ⏭️  Skipping local/relative link")
            continue
        
        if test_url(url):
            print(f"  ✅ Working")
            continue
        
        print(f"  ❌ Broken - looking for replacement...")
        replacement = None
        
        # Wikipedia-specific fixes
        if 'wikipedia.org' in url and '/wiki/' in url:
            topic = url.split('/wiki/')[-1]
            print(f"  🔍 Searching for Wikipedia topic: {topic}")
            replacement = find_wikipedia_alternatives(topic)
        
        # Unsplash fixes
        elif 'unsplash.com' in url:
            if '/photos/' in url:
                # Try to extract photo ID and create simpler URL
                photo_id_match = re.search(r'/photos/[^/]+-([a-zA-Z0-9_-]+)$', url)
                if photo_id_match:
                    photo_id = photo_id_match.group(1)
                    simple_url = f"https://unsplash.com/photos/{photo_id}"
                    print(f"  🔍 Trying simpler Unsplash URL: {simple_url}")
                    if test_url(simple_url):
                        replacement = simple_url
            
            # For photographer pages, suggest removal or generic Unsplash
            elif '/@' in url:
                print(f"  💡 Suggestion: Remove photographer attribution or use https://unsplash.com")
                replacement = "https://unsplash.com"
        
        if replacement:
            print(f"  ✅ Found replacement: {replacement}")
            old_link = f"[{text}]({url})"
            new_link = f"[{text}]({replacement})"
            content = content.replace(old_link, new_link)
            changes_made.append(f"'{url}' -> '{replacement}'")
        else:
            print(f"  ❌ No automatic replacement found")
            changes_made.append(f"MANUAL REVIEW NEEDED: '{url}' (text: '{text}')")
    
    # Write changes if any were made
    if content != original_content:
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"\n💾 Created backup: {backup_path}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Updated {file_path}")
        print(f"📝 Changes made:")
        for change in changes_made:
            print(f"  • {change}")
    else:
        print(f"\n✅ No broken links found or no fixes available")

def main():
    if len(sys.argv) != 2:
        print("Usage: python link_fixer.py <markdown_file_path>")
        print("Example: python link_fixer.py ../content/posts/indoor-herb-garden.md")
        sys.exit(1)
    
    file_path = sys.argv[1]
    fix_links_in_file(file_path)

if __name__ == "__main__":
    main()
