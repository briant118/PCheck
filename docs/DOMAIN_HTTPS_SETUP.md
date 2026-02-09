# How to Set Up Domain + Reverse Proxy (HTTPS)

This guide walks you through giving PCheck a proper web URL (e.g. `https://ilab.psu.palawan.edu.ph`) so students can access it from the internet. Everything described here is **free** (Nginx, Let's Encrypt, and a subdomain from your school).

---

## Setup order (do in this sequence)

1. **Get a domain** – Ask IT for a subdomain (e.g. `ilab.psu.palawan.edu.ph`) and have them point DNS to your server’s IP (the PC where PCheck runs).
2. **Run PCheck** – Daphne should be running on port 8000. When using a reverse proxy, run it as: `daphne -b 127.0.0.1 -p 8000 PCheckMain.asgi:application` so only the proxy can reach it.
3. **Install the reverse proxy** – Nginx (Linux or Windows) or IIS (Windows).
4. **Get an SSL certificate** – Let’s Encrypt (free) or from your school; bind it to the domain.
5. **Update `.env`** – Add the domain to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`, then restart Daphne.

---

## Option A: Nginx on Linux (Ubuntu/Debian)

### 1. Install Nginx and Certbot

```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2. Create the site config

Replace `ilab.psu.palawan.edu.ph` with your domain and `/path/to/PCheck` with your project path (e.g. `/home/ict/pcheck`).

```bash
sudo nano /etc/nginx/sites-available/pcheck
```

Paste this (then fix the paths and domain):

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

### 3. Enable the site and test

```bash
sudo ln -s /etc/nginx/sites-available/pcheck /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Get free HTTPS with Let's Encrypt

Your server must be reachable from the internet on port 80. Run:

```bash
sudo certbot --nginx -d ilab.psu.palawan.edu.ph
```

Follow the prompts (email, agree to terms). Certbot will add HTTPS and redirect HTTP to HTTPS.

### 5. Update PCheck `.env` and restart Daphne

In the PCheck project folder, edit `.env` and add your domain:

```env
ALLOWED_HOSTS=ilab.psu.palawan.edu.ph,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://ilab.psu.palawan.edu.ph,http://ilab.psu.palawan.edu.ph
```

Restart Daphne. Students can then use **https://ilab.psu.palawan.edu.ph**.

---

## Option B: Nginx on Windows

### 1. Download Nginx

- Go to [nginx.org/en/download.html](https://nginx.org/en/download.html).
- Download the stable Windows version and extract it (e.g. `C:\nginx`).

### 2. Create the config

- In the Nginx folder, open `conf\nginx.conf` and inside the `http { ... }` block add:  
  `include sites/*.conf;`
- Create the folder `conf\sites` and create `conf\sites\pcheck.conf` with the same `server { ... }` block as in Option A.
- Use Windows paths for `alias`, with forward slashes, e.g.:
  - `alias C:/path/to/PCheck/staticfiles/;`
  - `alias C:/path/to/PCheck/media/;`

### 3. Run Nginx

From the Nginx folder (e.g. `C:\nginx`):

```cmd
start nginx
```

To reload after changes: `nginx -s reload`.

### 4. SSL on Windows

- **If your school gives you an SSL certificate:** Configure Nginx with a `listen 443 ssl;` server block and the `ssl_certificate` and `ssl_certificate_key` paths.
- **Free certificate:** Use [win-acme](https://www.win-acme.com/) to get a Let's Encrypt certificate, then point Nginx at the generated certificate files.

### 5. Update PCheck `.env`

Same as Option A: add your domain to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`, then restart Daphne.

---

## Option C: IIS on Windows

1. **Install IIS** – Turn Windows features on → Internet Information Services. Also install **URL Rewrite** and **ARR** (Application Request Routing) so IIS can proxy to Daphne.
2. **Create a site** – In IIS Manager, create a site with hostname `ilab.psu.palawan.edu.ph`.
3. **Proxy to Daphne** – Add a URL Rewrite rule to forward requests to `http://127.0.0.1:8000`. Set up virtual directories or rules for `/static/` and `/media/` to point to your project’s `staticfiles` and `media` folders.
4. **HTTPS** – Bind an SSL certificate to the site (from your school or from [win-acme](https://www.win-acme.com/) for Let's Encrypt).
5. **Update PCheck `.env`** – Add the domain to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`, then restart Daphne.

---

## Firewall and DNS

- **Server firewall:** Allow inbound **port 80 (HTTP)** and **port 443 (HTTPS)**. You can leave port 8000 closed so only Nginx/IIS talks to Daphne.
- **IT/DNS:** Ensure the domain (e.g. `ilab.psu.palawan.edu.ph`) points to your server’s IP and that students (on campus or internet) can reach that IP on ports 80 and 443.

---

## Summary

| Step | What to do |
|------|------------|
| 1 | Get domain from IT; DNS → your server IP |
| 2 | Run Daphne on `127.0.0.1:8000` |
| 3 | Install Nginx (or IIS) and add the proxy config |
| 4 | Get SSL (Let's Encrypt or school) and enable HTTPS |
| 5 | Add domain to `.env`, restart Daphne |

After that, everyone (ICT and students) can use **https://ilab.psu.palawan.edu.ph** from anywhere.
