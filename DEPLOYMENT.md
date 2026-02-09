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
| ICT staff        | Browser (internal or web URL)           | Same as above or `https://ilab.psu.palawan.edu.ph` |
| Students on campus | **Web** (campus WiFi / anywhere)      | `https://ilab.psu.palawan.edu.ph`    |

The server can be a Windows PC or a Linux machine. Students need a **domain name** (e.g. `ilab.psu.palawan.edu.ph`) that points to your server and is reachable from campus (and optionally the internet). Your IT team typically provides the domain and SSL certificate.

---

## Student access via the internet

Right now, only devices on the **same network** as the server can use `http://SERVER_IP:8000`. For students to open PCheck **from the internet** (campus WiFi, home, or anywhere), they need a **public URL**. You can do that in two ways:

| Option | Best for | What you need |
|--------|----------|----------------|
| **1. Domain + reverse proxy (HTTPS)** | Real deployment (ICT + students) | A domain (e.g. `ilab.psu.palawan.edu.ph`) from IT, Nginx or IIS on the server, SSL certificate. See Step 4 below. |
| **2. Tunnel (ngrok or Cloudflare Tunnel)** | Testing or when you don’t have a domain yet | A free account; run a small program that gives you a public HTTPS URL to your running Daphne. |

- **Option 1** – IT points the domain to your server’s IP (campus or public). You run Nginx or IIS with HTTPS and proxy to Daphne. Students use `https://ilab.psu.palawan.edu.ph`. This is the right long-term setup.
- **Option 2** – You run a tunnel (e.g. ngrok) on the same PC where Daphne runs. You get a URL like `https://abc123.ngrok-free.app`. Add that host to `.env` (`ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`), restart Daphne, and share the URL with students. No domain or reverse proxy needed; good for demos or until you have a domain.

**Quick tunnel (ngrok) for internet access:**  
1. Sign up at [ngrok.com](https://ngrok.com) and install ngrok.  
2. Start PCheck (Daphne) on port 8000.  
3. In another terminal run: `ngrok http 8000`.  
4. Copy the HTTPS URL (e.g. `https://abc123.ngrok-free.app`).  
5. In `.env` add it to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` (comma-separated), then restart Daphne.  
6. Students open that URL from anywhere. (PCheck already has middleware to skip the ngrok warning page.)

---

## What You Need

- **A computer to run PCheck**: You do **not** need a dedicated “full” server. A regular PC (desktop or laptop) on the campus network is enough—the same machine where you install Python, MySQL, and run Daphne. Use a “real” server only if you need 24/7 uptime or very high traffic. For ICT lab + student booking, an ordinary PC is fine.
- **Domain name**: A hostname for students (e.g. `ilab.psu.palawan.edu.ph`). IT sets DNS to point this to your server’s IP.
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
ALLOWED_HOSTS=ilab.psu.palawan.edu.ph,10.30.130.178,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://ilab.psu.palawan.edu.ph,http://10.30.130.178:8000
```

- Replace `ilab.psu.palawan.edu.ph` with your actual **public/campus domain**.
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

**Full step-by-step guide:** See **docs/DOMAIN_HTTPS_SETUP.md** for a detailed walkthrough (Nginx on Linux/Windows, IIS, SSL, and `.env`).

To give students a **normal web URL** (e.g. `https://ilab.psu.palawan.edu.ph`), put a **reverse proxy** in front of Daphne. The proxy handles the domain, HTTPS, and serves static files; it forwards other requests to Daphne.

### Setup order (do in this sequence)

1. **Get a domain** – Ask IT for a subdomain (e.g. `ilab.psu.palawan.edu.ph`) and have them point DNS to your server’s IP (the PC where PCheck runs).
2. **Ensure PCheck runs** – Daphne should be running on port 8000 (e.g. `daphne -b 127.0.0.1 -p 8000 ...`). Use `127.0.0.1` so only the proxy talks to it.
3. **Install the reverse proxy** – Nginx (Linux or Windows) or IIS (Windows).
4. **Get an SSL certificate** – Let’s Encrypt (free) or from your school; bind it to the domain.
5. **Update `.env`** – Add the domain to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` (e.g. `https://ilab.psu.palawan.edu.ph`), then restart Daphne.

---

### Option A: Nginx (Linux) – step by step

1. Install Nginx and (if you use Let’s Encrypt) Certbot.
2. Create a config for your domain (e.g. `/etc/nginx/sites-available/pcheck`):

```nginx
server {
    listen 80;
    server_name ilab.psu.palawan.edu.ph;
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

**3. Enable the site and test**

```bash
sudo ln -s /etc/nginx/sites-available/pcheck /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**4. Get free HTTPS with Let's Encrypt**

Your server must be reachable from the internet on port 80. Run:

```bash
sudo certbot --nginx -d ilab.psu.palawan.edu.ph
```

Follow the prompts (email, agree to terms). Certbot will add HTTPS and redirect HTTP to HTTPS.

**5. Update PCheck `.env` and restart Daphne**

In the PCheck folder, edit `.env` and add your domain:

```env
ALLOWED_HOSTS=ilab.psu.palawan.edu.ph,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://ilab.psu.palawan.edu.ph,http://ilab.psu.palawan.edu.ph
```

Restart Daphne. Students can then use **https://ilab.psu.palawan.edu.ph**.

### Option B: IIS (Windows)

1. Install **IIS** and **URL Rewrite**, and **ARR** (Application Request Routing) so IIS can proxy to Daphne.
2. Create a site in IIS with the hostname `ilab.psu.palawan.edu.ph`.
3. Add a **URL Rewrite** rule to forward requests to `http://127.0.0.1:8000`, and set up **Static Content** for `/static/` and `/media/` to the project’s `staticfiles` and `media` folders.
4. Bind an HTTPS certificate to the site (from your school or Let’s Encrypt with win-acme).

Detailed IIS steps depend on your Windows version; the idea is: **IIS handles the domain and HTTPS**, and **proxies to Daphne on 127.0.0.1:8000**.

---

## Step 5: Firewall and Network

- **Server firewall**: Allow:
  - **Port 80 (HTTP)** and **443 (HTTPS)** if you use Nginx/IIS (students use the web).
  - **Port 8000** only if you want ICT to use `http://SERVER_IP:8000` directly; otherwise you can leave 8000 closed and have everyone use the web URL.
- **Campus/IT**: Ensure the domain (e.g. `ilab.psu.palawan.edu.ph`) resolves to your server’s IP and that students on campus WiFi (and optionally off-campus) can reach that IP on 80/443.

---

## Step 6: Who Uses Which URL

- **ICT (centralized network)**  
  - Option 1: Use the **same web URL**: `https://ilab.psu.palawan.edu.ph` (easiest).  
  - Option 2: Use internal IP if you exposed port 8000: `http://10.30.130.178:8000`.

- **Students on campus**  
  - **Web only**: `https://ilab.psu.palawan.edu.ph` (or whatever domain you set). They open it in a browser for booking and login.

- **PowerShell client (lab PCs)**  
  - Use the server base URL, e.g. `-Server "http://10.30.130.178:8000"` or `-Server "https://ilab.psu.palawan.edu.ph"` if the script supports HTTPS.

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

Once IT gives you a domain and SSL, add it to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` and set up the reverse proxy so **students on campus can use the web** at `https://ilab.psu.palawan.edu.ph`.
