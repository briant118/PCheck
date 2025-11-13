# Session Management & Cleanup Flow

```mermaid
flowchart TD
    Start([System Running]) --> MiddlewareCheck[BookingCleanupMiddleware<br/>Runs on Each Request]
    
    MiddlewareCheck --> CheckExpired[Check for Expired Bookings:<br/>end_time < now<br/>expiry is null]
    CheckExpired --> FoundExpired{Found Expired?}
    
    FoundExpired -->|Yes| ProcessExpired[For Each Expired Booking]
    FoundExpired -->|No| CheckWarnings
    
    ProcessExpired --> FreePC[Set PC booking_status = 'available']
    FreePC --> UpdateExpiry[Set booking.expiry = end_time]
    UpdateExpiry --> RemoveWarning[Remove from Warning Set]
    RemoveWarning --> CheckWarnings
    
    CheckWarnings --> Check5Min[Check Bookings Ending in 5 Minutes:<br/>end_time between 4.5-5.5 min]
    Check5Min --> FoundWarnings{Found Warnings?}
    
    FoundWarnings -->|No| EndMiddleware[End Middleware]
    FoundWarnings -->|Yes| ProcessWarning[For Each Booking to Warn]
    
    ProcessWarning --> CheckWarned{Already Warned?}
    CheckWarned -->|Yes| EndMiddleware
    CheckWarned -->|No| CalculateTime[Calculate Minutes Remaining]
    
    CalculateTime --> GetPCName[Get PC Name]
    GetPCName --> GetChannelLayer[Get WebSocket Channel Layer]
    GetChannelLayer --> ChannelAvailable{Channel Available?}
    
    ChannelAvailable -->|No| LogError[Log Error]
    ChannelAvailable -->|Yes| SendWarning[Send WebSocket Message:<br/>- type: 'session_warning'<br/>- message: 'Session ends in X min'<br/>- minutes_left<br/>- show_popup: True]
    
    SendWarning --> AddToWarned[Add to Warned Set]
    AddToWarned --> EndMiddleware
    LogError --> EndMiddleware
    
    EndMiddleware --> RequestContinue[Continue Request Processing]
    RequestContinue --> End([Request Complete])
    
    ManualCleanup[Manual Cleanup via clearup_pcs] --> ManualCheck[Check Expired Bookings]
    ManualCheck --> ManualFree[Free PCs]
    ManualFree --> ManualUpdate[Update Booking Expiry]
    ManualUpdate --> ReturnJSON[Return JSON Response]
    
    EndSession[User/Staff Ends Session Early] --> EndSessionRequest[POST to end_session]
    EndSessionRequest --> ValidatePermission{Has Permission?}
    
    ValidatePermission -->|No| PermissionDenied[Return 403 Error]
    ValidatePermission -->|Yes| GetBooking[Get Booking by ID]
    
    GetBooking --> BookingExists{Booking Exists?}
    BookingExists -->|No| NotFound[Return 404 Error]
    BookingExists -->|Yes| FreePCManual[Set PC booking_status = 'available']
    
    FreePCManual --> CancelBooking[Set booking.status = 'cancelled']
    CancelBooking --> ReturnSuccess[Return Success Response]
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style SendWarning fill:#fff9c4
    style FreePC fill:#c8e6c9
    style PermissionDenied fill:#ffcdd2
    style NotFound fill:#ffcdd2
```

## Process Steps:

1. **Automatic Cleanup (Middleware)**
   - Runs on every request
   - Checks for expired bookings
   - Frees PCs automatically
   - Updates booking expiry timestamp

2. **Session Warnings**
   - Checks bookings ending in 5 minutes
   - Sends WebSocket warnings to PC
   - Tracks warned bookings to avoid duplicates
   - Shows popup notification on PC

3. **Manual Cleanup**
   - Staff can trigger cleanup manually
   - Clears all expired bookings
   - Returns status message

4. **Early Session End**
   - User or staff can end session early
   - Validates permissions
   - Frees PC immediately
   - Cancels booking

