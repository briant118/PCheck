# How PCheck Works: “Running Locally” but “Accessed via the Web”

This document explains how PCheck can run on one computer (locally) and still be reachable by users through a normal web URL (e.g. **http://ilab.psu.palawan.edu.ph**). It is intended for IT / network administrators.

---

## Short answer

- **“Running locally”** = The PCheck application runs on **one PC** (the “server” machine). No cloud server is required.
- **“Accessed by web”** = That same PC is on the network and has a **web server** listening. When someone opens **http://ilab.psu.palawan.edu.ph** in a browser, the network sends the request to that PC, and the browser gets the page back. So “locally” only means “on one machine”; access is still **via the web** (HTTP/HTTPS and a URL).

---

## What runs on the server PC

On the **one computer** that acts as the server, two things run:

1. **Nginx** (web server)  
   - Listens on **port 80** (and optionally **443** for HTTPS).  
   - Receives all requests to **http://ilab.psu.palawan.edu.ph** (or whatever subdomain you use).  
   - Serves static files (CSS, images) from disk.  
   - For everything else (login, booking, etc.), it **forwards** the request to the application.

2. **PCheck application (Daphne + Django)**  
   - Listens only on **127.0.0.1:8000** (localhost on that same PC).  
   - So it is **not** directly exposed to the network; only Nginx talks to it.  
   - It generates the pages and handles login, booking, and data.

So: **one physical PC**, with **Nginx** facing the network and **PCheck** running “locally” behind it on the same machine.

---

## How a user reaches the site (step by step)

1. A user (student/staff) opens a browser and goes to **http://ilab.psu.palawan.edu.ph**.
2. The browser asks DNS: “What IP address is **ilab.psu.palawan.edu.ph**?”
3. DNS returns the **IP of the server PC** (e.g. `10.30.130.178` or your assigned IP). That DNS record is what IT sets (subdomain → that IP).
4. The browser sends an HTTP request to **that IP, port 80** over the network (campus or internet, depending on your setup).
5. The **server PC** receives the request on port 80. **Nginx** is listening there; it handles the request.
6. For page content (login, dashboard, booking), Nginx **proxies** the request to **127.0.0.1:8000**, where **PCheck** is running. PCheck generates the response.
7. Nginx sends that response back to the user’s browser. The user sees the PCheck site.

So “running locally” = PCheck runs on one machine. “Accessed by web” = that machine is reachable by IP and the subdomain points to it, so users use a normal URL.

---

## Diagram (simplified)

```
[User’s browser]
       |
       | 1. Opens http://ilab.psu.palawan.edu.ph
       v
[DNS: ilab.psu.palawan.edu.ph → Server PC IP]
       |
       | 2. Request to Server IP, port 80
       v
[Server PC]
    |
    | 3. Nginx (port 80) receives request
    |
    | 4. For app pages: Nginx forwards to 127.0.0.1:8000
    v
    PCheck (Daphne/Django) on 127.0.0.1:8000
    |
    | 5. Response back through Nginx to user
    v
[User sees PCheck in browser]
```

---

## What IT needs to do

For the subdomain to work so that users can access PCheck “via the web” while it “runs locally” on that PC:

1. **DNS**  
   - Create a record for the subdomain (e.g. **ilab.psu.palawan.edu.ph**).  
   - **Type:** A (or CNAME if your setup uses it).  
   - **Value:** The **IP address of the PC** where Nginx and PCheck run (the “server” PC).  
   - So “ilab.psu.palawan.edu.ph” resolves to that one machine.

2. **Network / firewall**  
   - Ensure that the **server PC’s IP** is reachable from the networks where users are (e.g. campus WiFi, wired LAN, or internet if you want off‑campus access).  
   - Allow **inbound** traffic to that IP on **port 80** (HTTP) and, if you use HTTPS, **port 443**.

3. **No extra hardware**  
   - The “server” is just one PC (or laptop) on the network. No separate dedicated server is required unless you choose to use one.

---

## Summary for IT

| Question | Answer |
|----------|--------|
| Where does PCheck run? | On **one PC** (the “server” machine). |
| Is it “in the cloud”? | No. It runs on a machine on your network. |
| How do users open it? | By visiting **http://ilab.psu.palawan.edu.ph** (or your subdomain) in a browser. |
| How does the URL reach that PC? | DNS points the subdomain to that PC’s IP; users’ browsers connect to that IP on port 80. |
| What listens on port 80? | **Nginx** on that same PC. It serves the site and forwards app requests to PCheck on 127.0.0.1:8000. |
| What does IT need to do? | (1) Point the subdomain (DNS) to the server PC’s IP. (2) Allow traffic to that IP on ports 80 (and 443 if using HTTPS). |

So: **“Running locally”** = one computer runs the app. **“Accessed by web”** = that computer is reachable by URL because DNS points the subdomain to it and Nginx on that PC answers on the web ports.
