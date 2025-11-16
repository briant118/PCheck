# Next Steps After Ngrok Setup

## Step 1: Start Django Server

Open a terminal and run:
```bash
python manage.py runserver 8000
```

**OR** use the combined script:
```bash
START-DJANGO-AND-NGROK.bat
```

## Step 2: Start Ngrok

In a **new terminal window**, run:
```bash
START-NGROK.bat
```

**OR** if you prefer PowerShell:
```bash
.\START-NGROK.ps1
```

**OR** manually:
```bash
ngrok http 8000
```

## Step 3: Copy Your Ngrok URL

From the ngrok output, you'll see something like:
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok-free.app`)

## Step 4: Add Ngrok URL to Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **Credentials**
3. Click on your **OAuth 2.0 Client ID**
4. Scroll down to **Authorized redirect URIs**
5. Click **+ ADD URI**
6. Add this URL (replace with your actual ngrok URL):
   ```
   https://YOUR-NGROK-URL.ngrok-free.app/accounts/google/login/callback/
   ```
   **Important:** 
   - Use HTTPS (not HTTP)
   - Include the trailing slash `/`
   - Replace `YOUR-NGROK-URL` with your actual ngrok URL
7. Click **SAVE**

## Step 5: Update Django Site Configuration

Run this command:
```bash
python update_site_for_ngrok.py
```

This script will:
- Automatically detect your ngrok URL (if ngrok is running)
- Update your Django site configuration
- Show you the next steps

**OR** manually update in Django Admin:
1. Go to: `http://localhost:8000/admin/` (or your ngrok URL)
2. Navigate to **Sites** > **Sites**
3. Click on the default site (usually "example.com")
4. Update:
   - **Domain name**: `YOUR-NGROK-URL.ngrok-free.app` (without https://)
   - **Display name**: `PSU PCheck (Ngrok)`
5. Click **Save**

## Step 6: Update Social Application (if needed)

1. In Django Admin, go to **Social accounts** > **Social applications**
2. Click on your Google social application
3. Under **Sites**, make sure your site is selected
4. Click **Save**

## Step 7: Test Google OAuth

1. Open your browser
2. Go to: `https://YOUR-NGROK-URL.ngrok-free.app/accounts/login/`
3. Click **"Sign in with Google"**
4. You should be redirected to Google's login page
5. After logging in, you'll be redirected back to your app

## Troubleshooting

### "Invalid redirect_uri" error
- ✅ Make sure you added the ngrok URL to Google OAuth
- ✅ Wait 2-3 minutes after saving (Google needs time to update)
- ✅ Check the URL has trailing slash: `/callback/`
- ✅ Make sure it's HTTPS (not HTTP)

### Ngrok URL not detected
- Make sure ngrok is running
- Make sure Django server is running on port 8000
- Try manually entering the URL when running `update_site_for_ngrok.py`

### Site not updating
- Run `python update_site_for_ngrok.py` again
- Check Django admin: Sites > Sites
- Clear your browser cache

## Quick Reference

**Start everything:**
```bash
START-DJANGO-AND-NGROK.bat
```

**Update site after ngrok starts:**
```bash
python update_site_for_ngrok.py
```

**Access your app:**
```
https://YOUR-NGROK-URL.ngrok-free.app
```

## Important Notes

- ⚠️ **Free ngrok URLs change** each time you restart ngrok
- ⚠️ **Update Google OAuth** and Django site each time the URL changes
- ⚠️ **All devices** can now access using the ngrok URL
- ✅ **No IP addresses needed** - Google OAuth will work on all devices!

