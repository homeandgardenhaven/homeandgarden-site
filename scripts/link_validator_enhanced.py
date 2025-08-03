import requests
from bs4 import BeautifulSoup
import os
import sys
import re
from urllib.parse import urljoin, urlparse
import time

def find_replacement_link(broken_url, search_terms=None):
    """Try to find a working replacement for a broken link"""
    replacements = []
    
    # Common URL fixes
    if "wikipedia.org" in broken_url:
        # Try different Wikipedia URL patterns
        potential_fixes = []
        if "/wiki/" in broken_url:
            topic = broken_url.split("/wiki/")[-1]
            potential_fixes = [
                f"https://en.wikipedia.org/wiki/{topic}",
                f"https://en.wikipedia.org/wiki/{topic.replace('_', '-')}",
                f"https://en.wikipedia.org/wiki/{topic.replace('-', '_')}",
                f"https://simple.wikipedia.org/wiki/{topic}"
            ]
        
        for fix in potential_fixes:
            if fix != broken_url:
                try:
                    response = requests.head(fix, timeout=5, allow_redirects=True)
                    if response.status_code == 200:
                        replacements.append((fix, "Wikipedia URL pattern fix"))
                        break
                except:
                    continue
    
    # For Unsplash links that return 403, try alternative approaches
    elif "unsplash.com" in broken_url:
        if "/photos/" in broken_url:
            # Extract photo ID and try direct image access
            photo_id = broken_url.split("/photos/")[-1].split("-")[-1]
            alternative = f"https://unsplash.com/photos/{photo_id}"
            try:
                response = requests.head(alternative, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    replacements.append((alternative, "Simplified Unsplash URL"))
            except:
                pass
        
        # For author pages, suggest searching instead
        if "/@" in broken_url:
            author = broken_url.split("/@")[-1]
            alternative = f"https://unsplash.com/s/photos/{author}"
            replacements.append((alternative, f"Search for photographer {author} instead"))
    
    # Generic search-based replacements
    if not replacements and search_terms:
        # Try to find alternative sources
        search_alternatives = []
        
        for term in search_terms:
            # Suggest authoritative sources
            search_alternatives.extend([
                f"https://www.google.com/search?q={term.replace(' ', '+')}",
                f"https://en.wikipedia.org/wiki/Special:Search?search={term.replace(' ', '_')}",
            ])
        
        replacements.extend([(alt, "Search alternative") for alt in search_alternatives[:2]])
    
    return replacements

def extract_context_terms(soup, link_element):
    """Extract context terms around a link for better replacement suggestions"""
    if not link_element:
        return []
    
    # Get text content of the link
    link_text = link_element.get_text().strip()
    terms = [link_text] if link_text else []
    
    # Get surrounding text
    parent = link_element.parent
    if parent:
        parent_text = parent.get_text()
        # Extract meaningful words (remove common words)
        words = re.findall(r'\b[A-Za-z]{3,}\b', parent_text)
        terms.extend(words[:5])  # Take first 5 meaningful words
    
    return list(set(terms))  # Remove duplicates

def validate_links_enhanced(base_url):
    """Enhanced link validator with replacement suggestions"""
    try:
        print(f"🔍 Fetching page: {base_url}")
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links
        link_elements = soup.find_all('a', href=True)
        links = []
        link_contexts = {}
        
        for element in link_elements:
            href = element['href']
            if href.startswith('#'):  # Skip anchor links
                continue
            
            # Convert relative links to absolute
            if not href.startswith('http'):
                href = urljoin(base_url, href)
            
            links.append(href)
            link_contexts[href] = extract_context_terms(soup, element)
        
        print(f"📊 Found {len(links)} links to validate")
        
        broken_links = []
        working_links = 0
        
        for i, link in enumerate(links, 1):
            print(f"🔗 [{i}/{len(links)}] Checking: {link[:60]}{'...' if len(link) > 60 else ''}")
            
            try:
                # Try HEAD first (faster), then GET if that fails
                try:
                    link_response = requests.head(link, allow_redirects=True, timeout=10)
                except requests.RequestException:
                    link_response = requests.get(link, allow_redirects=True, timeout=10)
                
                if link_response.status_code >= 400:
                    context_terms = link_contexts.get(link, [])
                    replacements = find_replacement_link(link, context_terms)
                    broken_links.append((link, link_response.status_code, replacements))
                else:
                    working_links += 1
                    
            except requests.RequestException as e:
                context_terms = link_contexts.get(link, [])
                replacements = find_replacement_link(link, context_terms)
                broken_links.append((link, str(e), replacements))
            
            # Small delay to be respectful to servers
            time.sleep(0.1)
        
        # Report results
        print(f"\n📈 Results:")
        print(f"✅ Working links: {working_links}")
        print(f"❌ Broken links: {len(broken_links)}")
        
        if broken_links:
            print(f"\n💥 BROKEN LINKS WITH SUGGESTED FIXES:")
            print("=" * 80)
            
            for i, (link, error, replacements) in enumerate(broken_links, 1):
                print(f"\n{i}. ❌ BROKEN: {link}")
                print(f"   Error: {error}")
                
                if replacements:
                    print(f"   🔧 Suggested replacements:")
                    for replacement_url, reason in replacements:
                        print(f"      → {replacement_url}")
                        print(f"        Reason: {reason}")
                else:
                    print(f"   🤷 No automatic replacement found - manual review needed")
                print("-" * 80)
        else:
            print(f"\n🎉 All links are working!")
            
    except requests.RequestException as e:
        print(f"💥 Failed to fetch {base_url}: {e}")

def validate_all_posts(base_domain="http://localhost:1313"):
    """Validate links across all posts"""
    try:
        # Get sitemap or homepage to find all posts
        response = requests.get(base_domain)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all post links (adjust selector based on your theme)
        post_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/posts/' in href and href not in post_links:
                if not href.startswith('http'):
                    href = urljoin(base_domain, href)
                post_links.append(href)
        
        print(f"🗂️ Found {len(post_links)} posts to validate")
        
        for i, post_url in enumerate(post_links, 1):
            print(f"\n📄 [{i}/{len(post_links)}] Validating post: {post_url}")
            validate_links_enhanced(post_url)
            
    except Exception as e:
        print(f"💥 Error validating all posts: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            validate_all_posts()
        else:
            page_path = sys.argv[1]
            if page_path.startswith('/'):
                base_url = f"http://localhost:1313{page_path}"
            else:
                base_url = page_path
            validate_links_enhanced(base_url)
    else:
        # Default to homepage
        validate_links_enhanced("http://localhost:1313")
