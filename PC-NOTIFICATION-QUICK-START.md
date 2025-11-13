# PC Notification Monitor - Quick Start Guide

## 🚀 How to Use

### Option 1: Double-Click to Start (Easiest)
1. **Double-click** `START-PC-NOTIFICATIONS.bat`
2. The notification page will open automatically in fullscreen/kiosk mode
3. It will stay open and show warnings when 5 minutes are left

### Option 2: Run PowerShell Script
1. Right-click `START-PC-NOTIFICATIONS.ps1` → "Run with PowerShell"
2. Or open PowerShell and run: `.\START-PC-NOTIFICATIONS.ps1`

### Option 3: Auto-Start at Windows Login
1. Run `SETUP-AUTO-START-PC-NOTIFICATIONS.ps1` (as Administrator if needed)
2. The notification page will now open automatically every time you log in

## ⚙️ Configuration

### Set Your Server URL

**Method 1: Edit Config File (Recommended)**
1. Open `pc-notification-config.txt`
2. Change `SERVER_URL=http://192.168.137.238:8000` to your server IP
3. Save the file

**Method 2: Auto-Detection**
- The script will automatically try to find the server
- It checks your network adapters and common IP addresses
- If it can't find it, it uses `http://127.0.0.1:8000` (localhost)

**Method 3: Command Line**
```powershell
.\START-PC-NOTIFICATIONS.ps1 -ServerUrl "http://192.168.137.238:8000"
```

## 📋 Features

✅ **Auto-detects server URL** - No need to manually enter IP  
✅ **Auto-opens in kiosk mode** - Fullscreen, no browser UI  
✅ **Auto-start at login** - Set it up once, runs automatically  
✅ **Works with Chrome or Edge** - Uses whatever is available  
✅ **Shows PC name automatically** - Uses your computer name  

## 🔧 Troubleshooting

**Problem: Can't find server**
- Solution: Edit `pc-notification-config.txt` and set the correct server IP

**Problem: Browser doesn't open**
- Solution: Make sure Chrome or Edge is installed

**Problem: Page doesn't show warnings**
- Solution: 
  1. Check that the server is running
  2. Verify the PC name matches exactly (check the URL parameter)
  3. Open browser console (F12) to see connection status

**Problem: Want to see browser UI (not fullscreen)**
- Solution: Run with `-NoKiosk` flag:
  ```powershell
  .\START-PC-NOTIFICATIONS.ps1 -NoKiosk
  ```

## 📝 Notes

- The page must stay open to receive WebSocket warnings
- The popup will automatically appear when 5 minutes are left
- The page will go fullscreen when the warning appears
- Keep the browser window open and don't close the tab

