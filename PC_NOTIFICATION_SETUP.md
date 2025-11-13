# PC Session Warning Notification System

This feature displays a fullscreen popup warning on PCs when a session is about to end (5 minutes remaining), similar to how peripheral unplug notifications work.

## How It Works

1. **Middleware Monitoring**: The `BookingCleanupMiddleware` checks for bookings ending in 5 minutes on each request
2. **WebSocket Notification**: When a booking is 5 minutes from ending, a WebSocket message is sent to the PC
3. **PC Display**: The PC notification page receives the message and displays a fullscreen popup warning

## Setup Instructions

### On the Server (Already Configured)

The system is already set up with:
- WebSocket consumer for PC notifications (`PCNotificationConsumer`)
- Middleware that checks for bookings ending in 5 minutes
- HTML page for displaying notifications (`pc_notification.html`)
- URL route: `/pc-notification/?pc_name=PC_NAME`

### On Each PC

You need to open the notification page on each PC. There are two ways:

#### Option 1: Using the Provided Scripts

1. **Windows Batch Script** (`START-PC-NOTIFICATIONS.bat`):
   - Edit the script to set your server URL
   - Run it on each PC
   - It will open Chrome/Edge in kiosk mode

2. **PowerShell Script** (`START-PC-NOTIFICATIONS.ps1`):
   - Run: `.\START-PC-NOTIFICATIONS.ps1 -ServerUrl "http://your-server:8000" -PcName "PC-NAME"`
   - Or edit the default values in the script

#### Option 2: Manual Setup

1. Open a browser on the PC
2. Navigate to: `http://your-server:8000/pc-notification/?pc_name=PC-NAME`
   - Replace `your-server:8000` with your actual server URL
   - Replace `PC-NAME` with the actual PC name (usually `%COMPUTERNAME%` on Windows)
3. Press F11 for fullscreen (or use browser kiosk mode)

### Recommended: Auto-Start on Boot

To make the notification page start automatically when the PC boots:

1. **Windows Task Scheduler**:
   - Create a new task
   - Trigger: "At startup"
   - Action: Start a program
   - Program: Path to `START-PC-NOTIFICATIONS.bat` or browser executable
   - Arguments: `--kiosk --app=http://your-server:8000/pc-notification/?pc_name=%COMPUTERNAME%`

2. **Startup Folder**:
   - Copy `START-PC-NOTIFICATIONS.bat` to Windows Startup folder
   - Edit the script with your server URL

## Features

- **Fullscreen Popup**: Displays a prominent warning when 5 minutes remain
- **Auto-Reconnect**: WebSocket automatically reconnects if connection is lost
- **Status Indicator**: Shows connection status in the top-right corner
- **Auto-Close**: Popup automatically closes after 30 seconds (user can close earlier)
- **Responsive Design**: Works on different screen sizes

## Technical Details

### WebSocket Connection

- URL: `ws://your-server:8000/ws/pc-notifications/?pc_name=PC-NAME`
- Group: `pc_notifications_{PC_NAME}`
- Message Type: `session_warning`

### Notification Timing

- Checks for bookings ending between 4.5 and 5.5 minutes from now
- Only sends one warning per booking (tracked in middleware)
- Warning is sent when a request is made to the server during the warning window

### Message Format

```json
{
  "type": "session_warning",
  "message": "Your session will end in 5 minutes. Please save your work!",
  "minutes_left": 5,
  "end_time": "2025-01-01T12:00:00Z",
  "booking_id": 123,
  "pc_name": "PC-01"
}
```

## Troubleshooting

1. **No popup appears**:
   - Check that the PC notification page is open and connected (green status indicator)
   - Verify the PC name matches exactly (case-sensitive)
   - Check server logs for WebSocket connection messages

2. **Connection issues**:
   - Ensure WebSocket is enabled in Django Channels
   - Check firewall settings
   - Verify the server URL is correct

3. **Popup appears too early/late**:
   - The warning window is 4.5-5.5 minutes before end time
   - This ensures the warning is sent even if requests are infrequent

## Integration with Peripheral Watching

This uses the same WebSocket infrastructure as the peripheral watching system. The PC notification page can run alongside the peripheral watching script, or independently.

