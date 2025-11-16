# Ngrok Setup Guide for Google OAuth

This guide will help you set up ngrok to expose your local Django server so Google OAuth works on other devices. Google OAuth doesn't allow IP addresses in redirect URIs, so ngrok provides a public HTTPS URL.

## Prerequisites

1. A free ngrok account (sign up at https://dashboard.ngrok.com/signup)
2. ngrok installed on your system

## Step 1: Install Ngrok

### Windows:
1. Download ngrok from: https://ngrok.com/download
2. Extract the `ngrok.exe` file to a folder (e.g., `C:\ngrok\`)
3. Add the folder to your PATH environment variable, OR place it in your project folder

### Alternative: Using Chocolatey
```powershell
choco install ngrok
```

## Step 2: Get Your Ngrok Auth Token

1. Sign up or log in at https://dashboard.ngrok.com/
2. Go to "Your Authtoken" section
3. Copy your authtoken
4. Run this command to configure ngrok:
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

## Step 3: Start Your Django Server

First, make sure your Django server is running:
```bash
python manage.py runserver 8000
```

## Step 4: Start Ngrok

### Option A: Using the provided script (Recommended)
```bash
# Windows Command Prompt
START-NGROK.bat

# Windows PowerShell
.\START-NGROK.ps1
```

### Option B: Manual command
```bash
ngrok http 8000
```

This will give you output like:
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:8000
```

**Important:** Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

## Step 5: Update Google OAuth Settings

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" > "Credentials"
3. Click on your OAuth 2.0 Client ID
4. Under "Authorized redirect URIs", add:
   ```
   https://YOUR-NGROK-URL.ngrok-free.app/accounts/google/login/callback/
   ```
   Replace `YOUR-NGROK-URL` with your actual ngrok URL (e.g., `abc123.ngrok-free.app`)
5. Click "Save"

## Step 6: Update Django Site Configuration

### Option A: Using the provided script (Recommended)
```bash
python update_site_for_ngrok.py
```
This will automatically update your Django site with the ngrok URL.

### Option B: Manual update via Django Admin
1. Start your Django server: `python manage.py runserver 8000`
2. Go to http://localhost:8000/admin/ (or your ngrok URL)
3. Navigate to "Sites" > "Sites"
4. Click on the default site (usually "example.com")
5. Update:
   - **Domain name**: `YOUR-NGROK-URL.ngrok-free.app` (without https://)
   - **Display name**: `PSU PCheck (Ngrok)`
6. Click "Save"

### Option C: Using Django shell
```python
python manage.py shell
```
Then run:
```python
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'YOUR-NGROK-URL.ngrok-free.app'
site.name = 'PSU PCheck (Ngrok)'
site.save()
```

## Step 7: Update Social Application in Django Admin

1. Go to Django Admin: http://localhost:8000/admin/
2. Navigate to "Social accounts" > "Social applications"
3. Click on your Google social application
4. Under "Sites", make sure your ngrok site is selected
5. Click "Save"

## Step 8: Test Google OAuth

1. Access your application via the ngrok URL: `https://YOUR-NGROK-URL.ngrok-free.app`
2. Go to the login page
3. Click "Sign in with Google"
4. You should be redirected to Google's login page
5. After authentication, you'll be redirected back to your app

## Important Notes

### Ngrok URL Changes
- **Free ngrok accounts**: The URL changes every time you restart ngrok (unless you have a paid plan)
- **Solution**: Use the `update_site_for_ngrok.py` script each time you restart ngrok, OR use a static domain with a paid ngrok plan

### Security
- Ngrok exposes your local server to the internet
- Only use this for development/testing
- Don't expose production servers this way
- Consider using ngrok's authentication features for additional security

### Multiple Devices
- Once ngrok is running, any device can access your app using the ngrok URL
- No need to add multiple IP addresses to Google OAuth
- All devices will use the same ngrok URL

## Troubleshooting

### "Invalid redirect_uri" error
- Make sure you added the ngrok URL to Google Cloud Console
- The URL must be HTTPS (ngrok provides HTTPS automatically)
- Include the trailing slash: `/accounts/google/login/callback/`
- Wait a few minutes after updating Google OAuth settings for changes to propagate

### Ngrok URL not working
- Make sure your Django server is running on port 8000
- Check that ngrok is forwarding to the correct port
- Try restarting ngrok

### Site configuration not updating
- Make sure you're updating the correct site (usually ID=1)
- Clear your browser cache
- Restart your Django server after updating the site

### "This site can't be reached" on ngrok URL
- Make sure ngrok is running
- Make sure your Django server is running
- Check that ngrok is forwarding to port 8000
- Try accessing the ngrok URL directly in your browser first

## Quick Start Scripts

The project includes these helper scripts:
- `START-NGROK.bat` - Windows batch script to start ngrok
- `START-NGROK.ps1` - Windows PowerShell script to start ngrok
- `update_site_for_ngrok.py` - Python script to automatically update Django site with ngrok URL

## Next Steps

1. Start Django server: `python manage.py runserver 8000`
2. Start ngrok: Run `START-NGROK.bat` or `START-NGROK.ps1`
3. Copy the ngrok HTTPS URL
4. Add it to Google OAuth redirect URIs
5. Run `python update_site_for_ngrok.py` to update Django site
6. Test Google OAuth login

