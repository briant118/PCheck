# PCheck – Deploy (Domain + HTTPS)

Use this folder when you want students to access PCheck via a **domain and HTTPS** (e.g. `https://ilab.psu.palawan.edu.ph`).

## What’s here

| File | Purpose |
|------|--------|
| **nginx-pcheck.conf** | Nginx config for PCheck. Use it with Nginx (Windows or Linux). |
| **start_daphne_behind_nginx.bat** / **.ps1** | Start PCheck (Daphne) on `127.0.0.1:8000` so only Nginx talks to it. |
| **setup_nginx_windows.ps1** | Optional: download Nginx for Windows and drop in the PCheck config. |
| **README.md** | This file. |

## Quick setup (Domain + HTTPS)

1. **Get a domain**  
   Ask IT for a subdomain (e.g. `ilab.psu.palawan.edu.ph`) and have DNS point to your server PC’s IP.

2. **Install Nginx**  
   - **Windows:** Run `.\deploy\setup_nginx_windows.ps1` from the PCheck folder, or download from [nginx.org/en/download.html](https://nginx.org/en/download.html) and use **nginx-pcheck.conf** as in docs/DOMAIN_HTTPS_SETUP.md.  
   - **Linux:** See docs/DOMAIN_HTTPS_SETUP.md (Option A).

3. **Start PCheck for Nginx**  
   Run **start_daphne_behind_nginx.bat** (or the .ps1 script). This starts Daphne on `127.0.0.1:8000` only.

4. **Start Nginx**  
   If you used the setup script: run `deploy\nginx\nginx.exe`. Otherwise start Nginx as you installed it.

5. **Get SSL (HTTPS)**  
   Use Let’s Encrypt (Certbot on Linux, or [win-acme](https://www.win-acme.com/) on Windows) or a certificate from your school. Point Nginx at the certificate and enable `listen 443 ssl`.

6. **Update .env**  
   In the PCheck folder, edit `.env` and add your domain:
   ```env
   ALLOWED_HOSTS=ilab.psu.palawan.edu.ph,127.0.0.1,localhost
   CSRF_TRUSTED_ORIGINS=https://ilab.psu.palawan.edu.ph,http://ilab.psu.palawan.edu.ph
   ```
   Then restart Daphne.

After that, everyone can use **https://ilab.psu.palawan.edu.ph**.

## Editing nginx-pcheck.conf

- Replace **ilab.psu.palawan.edu.ph** with your domain.
- Replace the **alias** paths with your actual PCheck path (the one that contains `staticfiles` and `media`). Use forward slashes and quotes if the path has spaces.
