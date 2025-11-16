# How to Access PCheck from Other Devices

## Your Ngrok URL
```
https://lorena-unbrave-heteronymously.ngrok-free.dev
```

## Quick Steps

### 1. Make Sure Servers Are Running

**On your main computer:**
- ✅ Django server: `python manage.py runserver 8000`
- ✅ Ngrok: `START-NGROK.bat` (or `ngrok http 8000`)

### 2. Access from Any Device

**On your phone, tablet, or another computer:**

1. Open any web browser (Chrome, Safari, Firefox, etc.)
2. Go to: `https://lorena-unbrave-heteronymously.ngrok-free.dev`
3. The PCheck application will load!

### 3. Login with Google OAuth

1. Click "Sign in with Google"
2. Google OAuth will work because ngrok provides HTTPS
3. No IP addresses needed!

## Device-Specific Instructions

### 📱 Android Phone/Tablet
1. Open Chrome or any browser
2. Type: `https://lorena-unbrave-heteronymously.ngrok-free.dev`
3. Bookmark it for easy access

### 🍎 iPhone/iPad
1. Open Safari or any browser
2. Type: `https://lorena-unbrave-heteronymously.ngrok-free.dev`
3. Add to Home Screen for app-like experience

### 💻 Another Computer
1. Open any browser
2. Type: `https://lorena-unbrave-heteronymously.ngrok-free.dev`
3. Works on Windows, Mac, Linux

## Important Notes

### ⚠️ Ngrok URL Changes
- **Free ngrok URLs change** each time you restart ngrok
- If you restart ngrok, you'll get a new URL
- Update Google OAuth redirect URI with the new URL
- Update Django site: `python update_site_simple.py`

### ✅ What Works
- ✅ Access from anywhere (not just local network)
- ✅ Google OAuth works on all devices
- ✅ HTTPS is provided by ngrok
- ✅ No IP address configuration needed
- ✅ Works on mobile, tablet, desktop

### 🔒 Security Note
- Ngrok exposes your local server to the internet
- Only use for development/testing
- Don't use for production
- Consider ngrok authentication for additional security

## Troubleshooting

### "This site can't be reached"
- ✅ Make sure Django server is running
- ✅ Make sure ngrok is running
- ✅ Check internet connection on both devices
- ✅ Try the URL in a different browser

### "Ngrok warning page"
- This is normal for free ngrok accounts
- Click "Visit Site" button to proceed
- You can upgrade to paid plan to remove this

### Google OAuth not working
- ✅ Make sure ngrok URL is added to Google OAuth redirect URIs
- ✅ Wait 2-3 minutes after updating Google OAuth settings
- ✅ Check the URL has trailing slash: `/callback/`

### Slow loading
- Ngrok free tier has some limitations
- Connection speed depends on your internet
- Consider upgrading to paid ngrok plan for better performance

## Quick Reference

**Your current ngrok URL:**
```
https://lorena-unbrave-heteronymously.ngrok-free.dev
```

**Login page:**
```
https://lorena-unbrave-heteronymously.ngrok-free.dev/accounts/login/
```

**To update site after ngrok URL changes:**
```bash
python update_site_simple.py
```

## Sharing with Others

You can share this URL with:
- ✅ Team members
- ✅ Testers
- ✅ Clients (for demos)
- ✅ Anyone who needs to access the app

**Just make sure:**
- Your computer is running
- Django server is running
- Ngrok is running
- They have internet connection

