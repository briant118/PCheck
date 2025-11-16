# Fix Google OAuth Redirect URI Mismatch Error

## Error: redirect_uri_mismatch

This error means the redirect URI in Google Cloud Console doesn't match what Django is sending.

## Quick Fix Steps

### Step 1: Update Django Site Domain

The Django site domain MUST match your ngrok URL. Run:

```bash
python update_site_simple.py
```

When prompted, enter: `lorena-unbrave-heteronymously.ngrok-free.dev`

**OR** manually update in Django Admin:
1. Go to: `https://lorena-unbrave-heteronymously.ngrok-free.dev/admin/`
2. Navigate to **Sites** > **Sites**
3. Click on the site (usually ID=1)
4. Update:
   - **Domain name**: `lorena-unbrave-heteronymously.ngrok-free.dev` (NO https://, NO trailing slash)
   - **Display name**: `PSU PCheck (Ngrok)`
5. Click **Save**

### Step 2: Add Exact Redirect URI to Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your **OAuth 2.0 Client ID**
3. Scroll to **Authorized redirect URIs**
4. Click **+ ADD URI**
5. Add this EXACT URL:
   ```
   https://lorena-unbrave-heteronymously.ngrok-free.dev/accounts/google/login/callback/
   ```
   **CRITICAL:**
   - ✅ Must be HTTPS (not HTTP)
   - ✅ Must have trailing slash `/` at the end
   - ✅ Must match exactly (no extra spaces, no typos)
6. Click **SAVE**
7. **Wait 2-3 minutes** for Google to update

### Step 3: Verify Social Application in Django Admin

1. Go to: `https://lorena-unbrave-heteronymously.ngrok-free.dev/admin/`
2. Navigate to **Social accounts** > **Social applications**
3. Click on your Google social application
4. Under **Sites**, make sure your site is selected
5. Click **Save**

### Step 4: Restart Django Server

**IMPORTANT:** Restart your Django server after making changes:

1. Stop Django (Ctrl+C)
2. Start again:
   ```bash
   python manage.py runserver 8000
   ```

### Step 5: Test Again

1. Go to: `https://lorena-unbrave-heteronymously.ngrok-free.dev/accounts/login/`
2. Click "Sign in with Google"
3. Should work now!

## Common Mistakes

### ❌ Wrong Domain Format
- ❌ `https://lorena-unbrave-heteronymously.ngrok-free.dev` (with https://)
- ✅ `lorena-unbrave-heteronymously.ngrok-free.dev` (without https://)

### ❌ Missing Trailing Slash
- ❌ `https://...ngrok-free.dev/accounts/google/login/callback` (no trailing slash)
- ✅ `https://...ngrok-free.dev/accounts/google/login/callback/` (with trailing slash)

### ❌ Wrong Protocol
- ❌ `http://lorena-unbrave-heteronymously.ngrok-free.dev/...` (HTTP)
- ✅ `https://lorena-unbrave-heteronymously.ngrok-free.dev/...` (HTTPS)

### ❌ Site Not Updated
- Make sure Django site domain matches ngrok URL exactly
- Restart Django after updating site

## Verify What Django Is Sending

To see what redirect URI Django is actually sending:

1. Go to: `https://lorena-unbrave-heteronymously.ngrok-free.dev/accounts/google/login/`
2. Look at the URL in your browser's address bar
3. It should contain `redirect_uri=...`
4. Copy that redirect_uri value
5. Make sure it EXACTLY matches what's in Google Cloud Console

## Still Not Working?

1. **Double-check the exact URL** in Google Cloud Console
2. **Wait 3-5 minutes** after saving (Google needs time to update)
3. **Clear browser cache** and try again
4. **Check Django site domain** matches ngrok URL exactly
5. **Restart Django server** after any changes
6. **Verify ngrok is still running** and URL hasn't changed

## If Ngrok URL Changes

If you restart ngrok and get a new URL:

1. Update Django site: `python update_site_simple.py`
2. Add new URL to Google OAuth redirect URIs
3. Update CSRF trusted origins: `python update_csrf_origins.py`
4. Restart Django server

