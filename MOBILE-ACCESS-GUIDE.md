# Mobile Access Guide - Access PCheck from Your Phone

## Quick Start

1. **Start the server** using one of these methods:
   - Double-click `START-SERVER-FOR-PHONE.bat` (Windows)
   - Or run `START-SERVER-FOR-PHONE.ps1` (PowerShell)

2. **Note your computer's IP address** (shown when server starts)
   - Most likely: `192.168.100.20`
   - Or check the output for other IPs

3. **Connect your phone to the same WiFi network** as your computer

4. **On your phone's browser**, go to:
   ```
   http://192.168.100.20:8000
   ```
   (Replace with your actual IP address)

## Finding Your IP Address

### Method 1: Using the Script
Run `START-SERVER-FOR-PHONE.bat` - it will show your IP addresses

### Method 2: Manual Check
1. Open Command Prompt
2. Type: `ipconfig`
3. Look for "IPv4 Address" under your active network adapter
4. Use that IP address (usually starts with 192.168.x.x)

## Troubleshooting

### Can't Access from Phone?

1. **Check Firewall**
   - Windows may block the connection
   - Go to: Windows Defender Firewall → Allow an app through firewall
   - Add Python or allow port 8000

2. **Check Network**
   - Phone and computer must be on the SAME WiFi network
   - Not on mobile data or different WiFi

3. **Check IP Address**
   - Make sure you're using the correct IP (not 127.0.0.1 or localhost)
   - Try all IP addresses shown in the script output

4. **Check Server is Running**
   - Make sure the server started successfully
   - Look for "Starting server" message

### Firewall Fix (Quick)

If firewall is blocking:

1. Open PowerShell as Administrator
2. Run:
   ```powershell
   New-NetFirewallRule -DisplayName "Django Server" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

Or temporarily disable Windows Firewall for testing (not recommended for production).

## Your Current IP Addresses

Based on your system:
- **192.168.100.20** ← Most likely this one (main network)
- 192.168.56.1 (VirtualBox/Hyper-V - ignore)
- 192.168.137.1 (Mobile Hotspot - ignore)

## Access URL

Use this on your phone:
```
http://192.168.100.20:8000
```

## Notes

- The server must be running on your computer
- Your computer must stay on and connected to WiFi
- If your IP changes, you'll need to use the new IP address
- For production, use a proper domain name and HTTPS

