"""
Script to automatically update Django site configuration with ngrok URL.
Run this after starting ngrok to update the site domain.
"""

import os
import sys
import django
import requests
from urllib.parse import urlparse

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PCheckMain.settings')
django.setup()

from django.contrib.sites.models import Site


def get_ngrok_url():
    """Get the ngrok URL from the ngrok API."""
    try:
        # Try to get ngrok URL from local API
        response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=2)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            for tunnel in tunnels:
                if tunnel.get('proto') == 'https':
                    public_url = tunnel.get('public_url', '')
                    if public_url:
                        # Remove https:// prefix
                        parsed = urlparse(public_url)
                        return parsed.netloc
    except Exception as e:
        print(f"Could not get ngrok URL from API: {e}")
    
    return None


def update_site(ngrok_domain):
    """Update the Django site with ngrok domain."""
    try:
        site = Site.objects.get(id=1)
        old_domain = site.domain
        site.domain = ngrok_domain
        site.name = 'PSU PCheck (Ngrok)'
        site.save()
        
        print("=" * 50)
        print("Site configuration updated successfully!")
        print("=" * 50)
        print(f"Old domain: {old_domain}")
        print(f"New domain: {ngrok_domain}")
        print(f"Full URL: https://{ngrok_domain}")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Make sure this URL is added to Google OAuth redirect URIs:")
        print(f"   https://{ngrok_domain}/accounts/google/login/callback/")
        print("2. Test Google OAuth login at:")
        print(f"   https://{ngrok_domain}/accounts/login/")
        print("=" * 50)
        
        return True
    except Site.DoesNotExist:
        print("ERROR: Site with ID=1 does not exist!")
        print("Please create a site in Django admin first.")
        return False
    except Exception as e:
        print(f"ERROR: Failed to update site: {e}")
        return False


def main():
    print("=" * 50)
    print("Django Site Updater for Ngrok")
    print("=" * 50)
    print()
    
    # Try to get ngrok URL automatically
    print("Attempting to detect ngrok URL...")
    ngrok_domain = get_ngrok_url()
    
    if not ngrok_domain:
        print("\nCould not automatically detect ngrok URL.")
        print("Please make sure:")
        print("1. Ngrok is running (run START-NGROK.bat or START-NGROK.ps1)")
        print("2. Ngrok is forwarding to port 8000")
        print()
        ngrok_domain = input("Enter your ngrok domain (e.g., abc123.ngrok-free.app): ").strip()
        
        if not ngrok_domain:
            print("ERROR: No domain provided. Exiting.")
            return
    
    # Remove https:// if user included it
    ngrok_domain = ngrok_domain.replace('https://', '').replace('http://', '').strip('/')
    
    # Update the site
    if update_site(ngrok_domain):
        print("\n✓ Site updated successfully!")
    else:
        print("\n✗ Failed to update site.")
        sys.exit(1)


if __name__ == '__main__':
    main()

