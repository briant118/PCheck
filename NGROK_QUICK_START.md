# Ngrok Quick Start Guide

## Quick Setup (5 minutes)

### 1. Install Ngrok
- Download from: https://ngrok.com/download
- Extract `ngrok.exe` to this project folder, OR add to PATH

### 2. Configure Ngrok
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```
Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken

### 3. Start Everything

**Terminal 1 - Django Server:**
```bash
python manage.py runserver 8000
```

**Terminal 2 - Ngrok:**
```bash
# Option A: Use the script
START-NGROK.bat

# Option B: Manual
ngrok http 8000
```

### 4. Copy Ngrok URL
From the ngrok output, copy the HTTPS URL:
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:8000
```

### 5. Update Google OAuth
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click your OAuth 2.0 Client ID
3. Add redirect URI: `https://YOUR-NGROK-URL.ngrok-free.app/accounts/google/login/callback/`
4. Save

### 6. Update Django Site
```bash
python update_site_for_ngrok.py
```

### 7. Test
Open: `https://YOUR-NGROK-URL.ngrok-free.app/accounts/login/`
Click "Sign in with Google" - it should work!

## Important Notes

- **Free ngrok URLs change** each time you restart ngrok
- **Update Google OAuth** and Django site each time the URL changes
- **Use the script** `update_site_for_ngrok.py` to automatically update Django site
- **All devices** can access using the ngrok URL - no IP addresses needed!

## Troubleshooting

**"Invalid redirect_uri"**
- Make sure you added the ngrok URL to Google OAuth
- Wait 2-3 minutes for Google to update
- Check the URL has trailing slash: `/callback/`

**Ngrok not working**
- Make sure Django is running on port 8000
- Check ngrok is forwarding correctly
- Try restarting both Django and ngrok

**Site not updating**
- Run `python update_site_for_ngrok.py` again
- Check Django admin: Sites > Sites
- Clear browser cache

## Full Documentation
See `NGROK_SETUP.md` for detailed instructions.

