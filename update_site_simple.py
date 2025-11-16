"""
Simple script to update Django site configuration with ngrok URL.
No external dependencies required.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PCheckMain.settings')
django.setup()

from django.contrib.sites.models import Site


def update_site(ngrok_domain):
    """Update the Django site with ngrok domain."""
    try:
        site = Site.objects.get(id=1)
        old_domain = site.domain
        site.domain = ngrok_domain
        site.name = 'PSU PCheck (Ngrok)'
        site.save()
        
        print("=" * 60)
        print("✓ Site configuration updated successfully!")
        print("=" * 60)
        print(f"Old domain: {old_domain}")
        print(f"New domain: {ngrok_domain}")
        print(f"Full URL: https://{ngrok_domain}")
        print("=" * 60)
        print("\n✓ Next steps:")
        print("1. Make sure this URL is added to Google OAuth redirect URIs:")
        print(f"   https://{ngrok_domain}/accounts/google/login/callback/")
        print("2. Test Google OAuth login at:")
        print(f"   https://{ngrok_domain}/accounts/login/")
        print("=" * 60)
        
        return True
    except Site.DoesNotExist:
        print("ERROR: Site with ID=1 does not exist!")
        print("Please create a site in Django admin first.")
        return False
    except Exception as e:
        print(f"ERROR: Failed to update site: {e}")
        return False


def main():
    print("=" * 60)
    print("Django Site Updater for Ngrok")
    print("=" * 60)
    print()
    
    # Get ngrok domain from user
    print("Enter your ngrok domain (e.g., lorena-unbrave-heteronymously.ngrok-free.dev)")
    print("Or press Enter to use the detected URL from your message:")
    ngrok_domain = input("Ngrok domain: ").strip()
    
    # If empty, use the one from the user's message
    if not ngrok_domain:
        ngrok_domain = "lorena-unbrave-heteronymously.ngrok-free.dev"
        print(f"Using: {ngrok_domain}")
    
    # Remove https:// if user included it
    ngrok_domain = ngrok_domain.replace('https://', '').replace('http://', '').strip('/')
    
    # Update the site
    if update_site(ngrok_domain):
        print("\n✓ Done! Your Django site is now configured for ngrok.")
    else:
        print("\n✗ Failed to update site.")
        sys.exit(1)


if __name__ == '__main__':
    main()

