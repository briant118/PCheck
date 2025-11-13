# PC Notification Troubleshooting Guide

## Issue: Popup Not Showing When Session is 5 Minutes Left

### Fixes Applied

1. **Fixed WebSocket message handler** - Removed the `show_popup` check requirement
2. **Added explicit `show_popup` flag** in middleware and consumer
3. **Improved logging** - Added debug prints to track warnings
4. **Added management command** - For periodic checking independent of requests

## How to Test

### Step 1: Verify PC Notification Page is Open

1. On the user PC, open the notification page:
   ```
   http://YOUR_SERVER:8000/pc-notification/?pc_name=PC-NAME
   ```
   Replace:
   - `YOUR_SERVER` with your server IP
   - `PC-NAME` with the exact PC name (case-sensitive)

2. Check the status indicator (top-right):
   - **Green "Connected"** = WebSocket is connected ✅
   - **Red "Disconnected"** = WebSocket connection failed ❌
   - **Yellow "Connecting"** = Still connecting...

3. Open browser console (F12) and check for:
   - `✅ PC Notification WebSocket connected: PC-NAME` (on server logs)
   - `WebSocket connected` (in browser console)

### Step 2: Verify Booking Has End Time

1. Check that the booking has:
   - `status = 'confirmed'`
   - `end_time` is set (not NULL)
   - `expiry` is NULL (not expired yet)

2. You can check in Django shell:
   ```python
   from main_app.models import Booking
   from django.utils import timezone
   from datetime import timedelta
   
   now = timezone.now()
   booking = Booking.objects.filter(status='confirmed', pc__name='PC-NAME').first()
   
   if booking:
       print(f"Booking ID: {booking.id}")
       print(f"End time: {booking.end_time}")
       print(f"Minutes until end: {(booking.end_time - now).total_seconds() / 60}")
   ```

### Step 3: Test the Warning Manually

#### Option A: Use Management Command (Recommended)

Run this command to manually trigger warnings:
```bash
python manage.py check_session_warnings
```

This will:
- Check all bookings ending in 5 minutes
- Send WebSocket warnings to connected PCs
- Show detailed output

#### Option B: Trigger via Request

The middleware checks on every request. To trigger it:
1. Make any request to the server (refresh any page)
2. Check server logs for: `⚠️ Session warning sent to PC: ...`

### Step 4: Check Server Logs

Look for these messages in your server console:

**When PC connects:**
```
✅ PC Notification WebSocket connected: PC-NAME
```

**When warning is sent:**
```
⚠️ Session warning sent to PC: PC-NAME (Booking ID: X, 5 min left)
   Message data: {...}
```

**When warning is received by PC:**
```
📤 Sending session warning to PC-NAME: {...}
```

### Step 5: Verify Timing

The warning is sent when:
- Booking `end_time` is between **4.5 and 5.5 minutes** from now
- Booking status is `'confirmed'`
- Booking `expiry` is NULL

**Important:** The middleware only runs when there's a request to the server. If no one is making requests, the warning won't be sent until someone accesses the site.

## Common Issues

### Issue 1: PC Name Mismatch

**Symptom:** WebSocket connects but warnings don't arrive

**Solution:** 
- PC name must match EXACTLY (case-sensitive)
- Check PC name in database: `PC.objects.get(name='...')`
- Check URL parameter: `?pc_name=EXACT-PC-NAME`

### Issue 2: WebSocket Not Connected

**Symptom:** Status shows "Disconnected"

**Solution:**
- Check server is running with WebSocket support (Daphne)
- Check firewall allows WebSocket connections (port 8000)
- Check browser console for connection errors
- Verify URL is correct: `ws://SERVER:8000/ws/pc-notifications/?pc_name=...`

### Issue 3: Warning Sent But Popup Doesn't Show

**Symptom:** Server logs show warning sent, but no popup

**Solution:**
- Check browser console for JavaScript errors
- Verify `data.type === 'session_warning'` in console
- Check if popup overlay exists: `document.getElementById('popupOverlay')`
- Try manually triggering: `showPopup({type: 'session_warning', minutes_left: 5})`

### Issue 4: Warning Not Sent (No Requests)

**Symptom:** No warning because no one is making requests

**Solution:**
- Use the management command: `python manage.py check_session_warnings`
- Set up a cron job/task scheduler to run it every minute
- Or make a request to the server when 5 minutes are left

## Setup Periodic Checking (Recommended)

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, repeat every 1 minute
4. Action: Start a program
5. Program: `python`
6. Arguments: `manage.py check_session_warnings`
7. Start in: `C:\path\to\your\project`

### Linux Cron

Add to crontab (`crontab -e`):
```
* * * * * cd /path/to/project && python manage.py check_session_warnings
```

This runs every minute.

## Debug Commands

### Check Active Bookings
```python
from main_app.models import Booking
from django.utils import timezone
from datetime import timedelta

now = timezone.now()
warning_start = now + timedelta(minutes=4, seconds=30)
warning_end = now + timedelta(minutes=5, seconds=30)

bookings = Booking.objects.filter(
    status='confirmed',
    end_time__gte=warning_start,
    end_time__lte=warning_end,
    expiry__isnull=True
)

for b in bookings:
    print(f"Booking {b.id}: PC={b.pc.name if b.pc else None}, End={b.end_time}")
```

### Check WebSocket Connections
Check server logs for:
- `✅ PC Notification WebSocket connected: ...`
- `❌ PC Notification WebSocket disconnected: ...`

### Test WebSocket Manually
In browser console on notification page:
```javascript
// Check connection
console.log('WebSocket state:', ws.readyState); // Should be 1 (OPEN)

// Manually trigger popup
showPopup({type: 'session_warning', minutes_left: 5, message: 'Test warning'});
```

## Still Not Working?

1. Check all the above steps
2. Verify PC name matches exactly
3. Check server logs for errors
4. Check browser console for JavaScript errors
5. Try the management command manually
6. Verify booking has correct end_time
7. Make sure WebSocket is connected (green status)

