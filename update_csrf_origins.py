"""
Script to update CSRF_TRUSTED_ORIGINS in settings.py with ngrok URL.
Run this whenever your ngrok URL changes.
"""

import re
import os

def update_csrf_origins(ngrok_url):
    """Update CSRF_TRUSTED_ORIGINS in settings.py"""
    settings_path = 'PCheckMain/settings.py'
    
    if not os.path.exists(settings_path):
        print(f"ERROR: {settings_path} not found!")
        return False
    
    # Read the settings file
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove https:// if included
    ngrok_domain = ngrok_url.replace('https://', '').replace('http://', '').strip('/')
    ngrok_full_url = f'https://{ngrok_domain}'
    
    # Pattern to match CSRF_TRUSTED_ORIGINS
    pattern = r"CSRF_TRUSTED_ORIGINS\s*=\s*\[(.*?)\]"
    
    # Check if CSRF_TRUSTED_ORIGINS exists
    if re.search(pattern, content, re.DOTALL):
        # Update existing CSRF_TRUSTED_ORIGINS
        def replace_csrf(match):
            existing = match.group(1)
            # Check if ngrok URL already exists
            if ngrok_full_url in existing:
                print(f"✓ Ngrok URL already in CSRF_TRUSTED_ORIGINS: {ngrok_full_url}")
                return match.group(0)
            
            # Remove old ngrok URLs (if any)
            lines = [line.strip() for line in existing.split('\n') if line.strip()]
            filtered_lines = [line for line in lines if 'ngrok-free.dev' not in line and 'ngrok.io' not in line]
            
            # Add new ngrok URL
            filtered_lines.append(f"    '{ngrok_full_url}',")
            
            # Keep localhost entries
            if not any('127.0.0.1' in line for line in filtered_lines):
                filtered_lines.append("    'http://127.0.0.1:8000',")
            if not any('localhost' in line for line in filtered_lines):
                filtered_lines.append("    'http://localhost:8000',")
            
            return f"CSRF_TRUSTED_ORIGINS = [\n" + "\n".join(filtered_lines) + "\n]"
        
        content = re.sub(pattern, replace_csrf, content, flags=re.DOTALL)
    else:
        # Add CSRF_TRUSTED_ORIGINS after ALLOWED_HOSTS
        csrf_config = f"""
# CSRF trusted origins - Add ngrok URLs here for Google OAuth to work
CSRF_TRUSTED_ORIGINS = [
    '{ngrok_full_url}',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]
"""
        # Find ALLOWED_HOSTS and add after it
        allowed_hosts_pattern = r"(ALLOWED_HOSTS\s*=\s*\[.*?\])"
        replacement = r"\1" + csrf_config
        content = re.sub(allowed_hosts_pattern, replacement, content, flags=re.DOTALL)
    
    # Write back to file
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("=" * 60)
    print("✓ CSRF_TRUSTED_ORIGINS updated successfully!")
    print("=" * 60)
    print(f"Added: {ngrok_full_url}")
    print("=" * 60)
    print("\n⚠️  IMPORTANT: Restart your Django server for changes to take effect!")
    print("=" * 60)
    
    return True


def main():
    print("=" * 60)
    print("CSRF Trusted Origins Updater for Ngrok")
    print("=" * 60)
    print()
    
    # Get ngrok URL from user
    print("Enter your ngrok URL (e.g., lorena-unbrave-heteronymously.ngrok-free.dev)")
    print("Or press Enter to use: lorena-unbrave-heteronymously.ngrok-free.dev")
    ngrok_url = input("Ngrok URL: ").strip()
    
    if not ngrok_url:
        ngrok_url = "lorena-unbrave-heteronymously.ngrok-free.dev"
        print(f"Using: {ngrok_url}")
    
    if update_csrf_origins(ngrok_url):
        print("\n✓ Done! Now restart your Django server.")
    else:
        print("\n✗ Failed to update CSRF_TRUSTED_ORIGINS.")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

