"""
Script to check what redirect URI Django is actually sending to Google.
This helps debug redirect_uri_mismatch errors.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PCheckMain.settings')
django.setup()

from django.contrib.sites.models import Site
from django.urls import reverse
from django.conf import settings

def check_redirect_uri():
    """Check what redirect URI Django will send to Google."""
    try:
        site = Site.objects.get(id=1)
        current_domain = site.domain
        
        # Build the redirect URI that Django will send
        # django-allauth uses: https://{domain}/accounts/google/login/callback/
        redirect_uri = f"https://{current_domain}/accounts/google/login/callback/"
        
        print("=" * 70)
        print("Google OAuth Redirect URI Checker")
        print("=" * 70)
        print()
        print(f"Current Django Site Domain: {current_domain}")
        print()
        print(f"Redirect URI Django will send to Google:")
        print(f"  {redirect_uri}")
        print()
        print("=" * 70)
        print("VERIFICATION CHECKLIST:")
        print("=" * 70)
        print()
        print("1. Go to Google Cloud Console:")
        print("   https://console.cloud.google.com/apis/credentials")
        print()
        print("2. Click on your OAuth 2.0 Client ID")
        print()
        print("3. Check 'Authorized redirect URIs' section")
        print()
        print(f"4. Make sure this EXACT URL is listed:")
        print(f"   {redirect_uri}")
        print()
        print("5. Important checks:")
        print("   ✓ Must be HTTPS (not HTTP)")
        print("   ✓ Must have trailing slash /")
        print("   ✓ Must match exactly (no typos)")
        print()
        print("6. If the URL is different or missing:")
        print("   - Click '+ ADD URI'")
        print(f"   - Add: {redirect_uri}")
        print("   - Click 'SAVE'")
        print("   - Wait 2-3 minutes for Google to update")
        print()
        print("=" * 70)
        
        # Check if it matches expected ngrok URL
        expected_ngrok = "lorena-unbrave-heteronymously.ngrok-free.dev"
        if current_domain != expected_ngrok:
            print()
            print("⚠️  WARNING: Site domain doesn't match expected ngrok URL!")
            print(f"   Current: {current_domain}")
            print(f"   Expected: {expected_ngrok}")
            print()
            print("   To fix, run:")
            print("   python update_site_simple.py")
            print()
        
        return redirect_uri
        
    except Site.DoesNotExist:
        print("ERROR: Site with ID=1 does not exist!")
        print("Please create a site in Django admin first.")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


if __name__ == '__main__':
    check_redirect_uri()

