# Google Authentication Setup Guide

This guide will help you set up Google OAuth2 authentication for the PCheck application.

## Prerequisites

1. A Google Cloud Platform account
2. Access to Google Cloud Console

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install `django-allauth==0.62.0` which handles Google authentication.

## Step 2: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google+ API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google+ API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
  - Add authorized redirect URIs:
    - `http://127.0.0.1:8000/accounts/google/login/callback/` (development)
    - `http://localhost:8000/accounts/google/login/callback/` (development)
    - `http://10.163.251.178:8000/accounts/google/login/callback/` (private IP - replace with your actual IP)
    - `http://192.168.x.x:8000/accounts/google/login/callback/` (local network IP - replace x.x with your actual IP)
    - `https://yourdomain.com/accounts/google/login/callback/` (production)
   - Click "Create"
   - Copy the **Client ID** and **Client Secret**

## Step 3: Configure Django Settings

Open `PCheck/PCheckMain/settings.py` and update the Google OAuth settings:

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
        'APP': {
            'client_id': 'YOUR_GOOGLE_CLIENT_ID',  # Replace with your Client ID
            'secret': 'YOUR_GOOGLE_CLIENT_SECRET',  # Replace with your Client Secret
            'key': ''
        }
    }
}
```

Replace `YOUR_GOOGLE_CLIENT_ID` and `YOUR_GOOGLE_CLIENT_SECRET` with your actual credentials.

## Step 4: Run Migrations

```bash
python manage.py migrate
```

This will create the necessary database tables for django-allauth.

## Step 5: Create a Site in Django Admin

1. Run the development server:
   ```bash
   python manage.py runserver
   ```
2. Go to http://127.0.0.1:8000/admin/
3. Navigate to "Sites" > "Sites"
4. Add or edit the default site:
   - Domain name: `127.0.0.1:8000` (for development) or your production domain
   - Display name: `PSU PCheck`

## Step 6: Add Google Social Application

1. In Django admin, go to "Social accounts" > "Social applications"
2. Click "Add social application"
3. Fill in the form:
   - Provider: `Google`
   - Name: `Google` (or any name you prefer)
   - Client id: Your Google Client ID
   - Secret key: Your Google Client Secret
   - Sites: Select your site (e.g., `127.0.0.1:8000`)
4. Click "Save"

## Step 7: Test the Integration

1. Start your Django server:
   ```bash
   python manage.py runserver
   ```
2. Navigate to the login page: http://127.0.0.1:8000/account/login/
3. Click "Sign in with Google"
4. You should be redirected to Google's login page
5. After successful authentication, you'll be redirected to the profile completion page

## How It Works

1. **User clicks "Sign in with Google"** → Redirected to Google OAuth
2. **User authenticates with Google** → Google redirects back to your app
3. **Profile completion** → If the user doesn't have a complete profile, they'll be asked to:
   - Select their role (Student/Faculty/Staff)
   - Select their college
   - Fill in additional details (course, year, block for students)
4. **Redirect** → User is redirected based on their role:
   - Staff → Dashboard
   - Student/Faculty → Home page

## Important Notes

- The system automatically extracts the `school_id` from PSU emails (`@psu.palawan.edu.ph`)
- For non-PSU emails, users can manually enter their school ID
- Profile completion is required before accessing the main application
- The system links existing accounts by email address

## Troubleshooting

### "Invalid redirect_uri" error
- Ensure the redirect URI in Google Cloud Console matches exactly:
  - Must include the trailing slash: `/accounts/google/login/callback/`
  - Must match the protocol (http vs https)
  - Must match the domain

### User not redirected to profile completion
- Check that the `CustomSocialAccountAdapter` is properly configured
- Verify `SOCIALACCOUNT_ADAPTER` setting in `settings.py`

### Profile not created
- Check Django signals in `account/signals.py`
- Verify the `save_user` method in `CustomSocialAccountAdapter`

### "device_id and device_name are required for private IP" error
This error occurs when accessing Google OAuth from a private IP address (like `10.163.251.178` or `192.168.x.x`). Google OAuth doesn't allow IP addresses in redirect URIs.

**Solution 1: Use Ngrok (Recommended)**
This is the best solution for development and testing on multiple devices.

1. **Set up ngrok** (see `NGROK_SETUP.md` for detailed instructions):
   - Install ngrok from https://ngrok.com/download
   - Start your Django server: `python manage.py runserver 8000`
   - Run `START-NGROK.bat` or `START-NGROK.ps1` to start ngrok
   - Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

2. **Add ngrok URL to Google OAuth:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to "APIs & Services" > "Credentials"
   - Click on your OAuth 2.0 Client ID
   - Under "Authorized redirect URIs", add:
     - `https://YOUR-NGROK-URL.ngrok-free.app/accounts/google/login/callback/`
   - Click "Save"

3. **Update Django site:**
   - Run: `python update_site_for_ngrok.py`
   - Or manually update in Django Admin: Sites > Sites > Edit domain

4. **Access your app:**
   - Use the ngrok URL: `https://YOUR-NGROK-URL.ngrok-free.app`
   - All devices can now access using this URL
   - Google OAuth will work on all devices

**Solution 2: Add Private IP (Not Recommended)**
Only works for one IP address at a time.

1. **Add your private IP redirect URI to Google Cloud Console:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to "APIs & Services" > "Credentials"
   - Click on your OAuth 2.0 Client ID
   - Under "Authorized redirect URIs", add:
     - `http://YOUR_PRIVATE_IP:8000/accounts/google/login/callback/`
     - Replace `YOUR_PRIVATE_IP` with your actual private IP (e.g., `10.163.251.178`)
   - Click "Save"

2. **Find your private IP address:**
   - Windows: Run `ipconfig` in Command Prompt and look for "IPv4 Address"
   - The IP shown in the error message is your private IP (e.g., `10.163.251.178`)

3. **Important:** You must add the exact redirect URI including:
   - The protocol (`http://` or `https://`)
   - The full IP address and port
   - The complete callback path: `/accounts/google/login/callback/`
   - The trailing slash is required

**Note:** If you're accessing from multiple private IPs (different networks), you'll need to add each one separately to Google Cloud Console, OR use ngrok (Solution 1) which works for all devices.

## Production Considerations

1. **Update redirect URIs** in Google Cloud Console for your production domain
2. **Set `DEBUG = False`** in production settings
3. **Use environment variables** for sensitive credentials:
   ```python
   import os
   'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
   'secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
   ```
4. **Enable HTTPS** - Google requires HTTPS in production
5. **Update `ALLOWED_HOSTS`** with your production domain

