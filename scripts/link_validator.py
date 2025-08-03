import requests
from bs4 import BeautifulSoup
import os
import sys

def validate_links(base_url):
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True)]

        broken_links = []
        cnt = 0
        for link in links:
            cnt += 1
            if not link.startswith('http'):
                link = os.path.join(base_url, link)  # Handle relative links
            try:
                link_response = requests.head(link, allow_redirects=True, timeout=5)
                if link_response.status_code != 200:
                    broken_links.append((link, link_response.status_code))
            except requests.RequestException as e:
                broken_links.append((link, str(e)))

        if broken_links:
            print("Broken Links:")
            for link, error in broken_links:
                print(f"❌ {link} - {error}")
        else:
            print(f"✅ All {cnt} links are valid.")

    except requests.RequestException as e:
        print(f"Failed to fetch {base_url}: {e}")

if __name__ == "__main__":
    # Default to homepage, but allow command line argument for different pages
    if len(sys.argv) > 1:
        page_path = sys.argv[1]
        if page_path.startswith('/'):
            base_url = f"http://localhost:1313{page_path}"
        else:
            base_url = page_path
    else:
        base_url = "http://localhost:1313"  # Default to homepage
    
    print(f"Validating links on: {base_url}")
    validate_links(base_url)

#http://localhost:1313/posts/indoor-herb-garden/


#checking for broken links seems more complicated than this python script is doing (b/c you need to spider through all the pages)