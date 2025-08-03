import requests
from bs4 import BeautifulSoup
import os

def validate_links(base_url):
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True)]

        broken_links = []
        for link in links:
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
            print("✅ All links are valid.")

    except requests.RequestException as e:
        print(f"Failed to fetch {base_url}: {e}")

if __name__ == "__main__":
    base_url = "http://localhost:1313"  # Update this to your local Hugo server URL
    validate_links(base_url)
