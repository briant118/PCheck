# Self-Hosted Deployment: PCheck for ICT + Students on Campus

This guide covers **self-hosting** PCheck on your own server (campus machine) so that:

- **ICT (centralized network)** – Lab PCs and staff use the server (internal IP or same web URL).
- **Students on campus** – Use the **web** (a public/campus URL in the browser) for booking and login.

One server runs the same Django app for both. No code changes are required beyond configuration.

---

## Overview

| Who              | How they access                         | Example URL                    |
|------------------|-----------------------------------------|--------------------------------|
| ICT lab PCs      | Centralized network (same LAN as server)| `http://10.30.130.178:8000` or the web URL |
| ICT staff        | Browser (internal or web URL)           | Same as above or `https://pcheck.psu.edu.ph` |
| Students on campus | **Web** (campus WiFi / anywhere)      | `https://pcheck.psu.edu.ph`    |

The server can be a Windows PC or a Linux machine. Students need a **domain name** (e.g. `pcheck.psu.edu.ph`) that points to your server and is reachable from campus (and optionally the internet). Your IT team typically provides the domain and SSL certificate.

---

## What You Need

- **A computer to run PCheck**: You do **not** need a dedicated “full” server. A regular PC (desktop or laptop) on the campus network is enough—the same machine where you install Python, MySQL, and run Daphne. Use a “real” server only if you need 24/7 uptime or very high traffic. For ICT lab + student booking, an ordinary PC is fine.
- **Domain name**: A hostname for students (e.g. `pcheck.psu.edu.ph`). IT sets DNS to point this to your server’s IP.
- **HTTPS (recommended)**: SSL certificate for the domain (e.g. from Let’s Encrypt or your school).
- **Reverse proxy**: Nginx (Linux) or IIS (Windows) to handle the domain, HTTPS, and to forward requests to Django.

---

## Step 1: Prepare the Server

1. **Install on the server** (same as “another PC”): Python 3.8+, MySQL, Git.  
   Follow **SETUP_ON_ANOTHER_PC.md** through: clone, venv, `pip install -r requirements.txt`, create DB, migrate, create superuser.

2. **Collect static files** (required for production):
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Do not use** `runserver` for production. Use **Daphne** (ASGI server) so the app listens on all interfaces and supports WebSockets.

---

## Step 2: Environment Variables for Production

On the server, create or edit `.env` in the project root (same folder as `manage.py`).

**Required for deployment:**

```env
SECRET_KEY=your-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=pcheck.psu.edu.ph,10.30.130.178,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://pcheck.psu.edu.ph,http://10.30.130.178:8000
```

- Replace `pcheck.psu.edu.ph` with your actual **public/campus domain**.
- Replace `10.30.130.178` with your **server’s IP** (so ICT and direct access work).
- Add any other hostnames or IPs users will use (e.g. `pcheck.yourschool.edu`).

**Optional (if you use them):**

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
```

Generate a strong `SECRET_KEY` (e.g. `python -c "import secrets; print(secrets.token_urlsafe(50))"`).

---

## Step 3: Run the App with Daphne

From the project root, with the virtual environment activated:

```bash
daphne -b 0.0.0.0 -p 8000 PCheckMain.asgi:application
```

- `-b 0.0.0.0` – listen on all interfaces (so ICT and external users can reach it).
- `-p 8000` – port (you can use another port if 8000 is in use).

**Keeping it running:**

- **Windows**: Run in a dedicated console, or use **NSSM** / **Windows Service** to run Daphne as a service.
- **Linux**: Use **systemd** or **supervisor** to run the command and restart on failure.

Example **systemd** unit (`/etc/systemd/system/pcheck.service`):

```ini
[Unit]
Description=PCheck Daphne ASGI
After=network.target mysql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/PCheck
Environment="PATH=/path/to/PCheck/venv/bin"
ExecStart=/path/to/PCheck/venv/bin/daphne -b 127.0.0.1 -p 8000 PCheckMain.asgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

If you use Nginx as reverse proxy (Step 4), Daphne can bind to `127.0.0.1:8000` so only Nginx talks to it. If you don’t use a reverse proxy yet, keep `-b 0.0.0.0` so users can hit `http://SERVER_IP:8000` directly.

---

## Step 4: Reverse Proxy and HTTPS (So Students Use the Web)

To give students a **normal web URL** (e.g. `https://pcheck.psu.edu.ph`), put a **reverse proxy** in front of Daphne. The proxy handles the domain, HTTPS, and serves static files; it forwards other requests to Daphne.

### Option A: Nginx (Linux)

1. Install Nginx and (if you use Let’s Encrypt) Certbot.
2. Create a config for your domain (e.g. `/etc/nginx/sites-available/pcheck`):

```nginx
server {
    listen 80;
    server_name pcheck.psu.edu.ph;
    # Redirect HTTP to HTTPS (after you have SSL)
    # return 301 https://$server_name$request_uri;
    # Until then, use this block to proxy:

    location /static/ {
        alias /path/to/PCheck/staticfiles/;
    }
    location /media/ {
        alias /path/to/PCheck/media/;
    }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

3. Enable the site and reload Nginx.  
4. Add HTTPS (e.g. `certbot --nginx -d pcheck.psu.edu.ph`). Then in the same `server` block add `listen 443 ssl;` and the `ssl_*` directives Certbot adds, and change the `listen 80` block to `return 301 https://...`.

Replace `/path/to/PCheck` with the real path to your project. After this, **students on campus** can open `https://pcheck.psu.edu.ph` for booking.

### Option B: IIS (Windows)

1. Install **IIS** and **URL Rewrite**, and **ARR** (Application Request Routing) so IIS can proxy to Daphne.
2. Create a site in IIS with the hostname `pcheck.psu.edu.ph`.
3. Add a **URL Rewrite** rule to forward requests to `http://127.0.0.1:8000`, and set up **Static Content** for `/static/` and `/media/` to the project’s `staticfiles` and `media` folders.
4. Bind an HTTPS certificate to the site (from your school or Let’s Encrypt with win-acme).

Detailed IIS steps depend on your Windows version; the idea is: **IIS handles the domain and HTTPS**, and **proxies to Daphne on 127.0.0.1:8000**.

---

## Step 5: Firewall and Network

- **Server firewall**: Allow:
  - **Port 80 (HTTP)** and **443 (HTTPS)** if you use Nginx/IIS (students use the web).
  - **Port 8000** only if you want ICT to use `http://SERVER_IP:8000` directly; otherwise you can leave 8000 closed and have everyone use the web URL.
- **Campus/IT**: Ensure the domain (e.g. `pcheck.psu.edu.ph`) resolves to your server’s IP and that students on campus WiFi (and optionally off-campus) can reach that IP on 80/443.

---

## Step 6: Who Uses Which URL

- **ICT (centralized network)**  
  - Option 1: Use the **same web URL**: `https://pcheck.psu.edu.ph` (easiest).  
  - Option 2: Use internal IP if you exposed port 8000: `http://10.30.130.178:8000`.

- **Students on campus**  
  - **Web only**: `https://pcheck.psu.edu.ph` (or whatever domain you set). They open it in a browser for booking and login.

- **PowerShell client (lab PCs)**  
  - Use the server base URL, e.g. `-Server "http://10.30.130.178:8000"` or `-Server "https://pcheck.psu.edu.ph"` if the script supports HTTPS.

---

## Checklist

- [ ] Server set up (Python, MySQL, clone, venv, migrate, superuser).
- [ ] `.env` on server: `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `SECRET_KEY`.
- [ ] `python manage.py collectstatic --noinput` run on server.
- [ ] Daphne runs (e.g. `daphne -b 0.0.0.0 -p 8000 PCheckMain.asgi:application` or behind Nginx with `127.0.0.1:8000`).
- [ ] Domain points to server; Nginx or IIS handles HTTPS and proxies to Daphne.
- [ ] Firewall allows 80/443 (and 8000 only if needed).
- [ ] Students use the web URL for booking; ICT uses the same URL or internal IP.

---

## Quick Test Without a Domain (ICT Only)

If you don’t have a domain yet:

1. On the server: set in `.env` only `DEBUG=False` and `ALLOWED_HOSTS=10.30.130.178,127.0.0.1,localhost` (use your server’s real IP).
2. Run: `daphne -b 0.0.0.0 -p 8000 PCheckMain.asgi:application`.
3. From another PC on the **same network** (e.g. ICT), open `http://10.30.130.178:8000`.

Once IT gives you a domain and SSL, add it to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` and set up the reverse proxy so **students on campus can use the web** at `https://pcheck.psu.edu.ph`.
