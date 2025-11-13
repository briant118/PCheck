# Student PC Booking Flow

```mermaid
flowchart TD
    Start([Student Logs In]) --> HomePage[Student Home Page]
    HomePage --> ViewAvailable[View Available PCs Count]
    ViewAvailable --> ClickReserve[Click 'Next' Button]
    ClickReserve --> ReservationPage[PC Reservation Page]
    
    ReservationPage --> DisplayPCs[Display Available PCs Grid]
    DisplayPCs --> SelectPC[Select PC from Grid]
    
    SelectPC --> CheckStatus{PC Status?}
    CheckStatus -->|In Repair| ShowRepair[Show Repair Message]
    CheckStatus -->|Offline| ShowOffline[Show Offline Message]
    CheckStatus -->|In Use| ShowInUse[Show In Use Details]
    CheckStatus -->|In Queue| ShowQueue[Show Queue Details]
    CheckStatus -->|Available| SelectDuration[Select Duration]
    
    ShowRepair --> DisplayPCs
    ShowOffline --> DisplayPCs
    ShowInUse --> DisplayPCs
    ShowQueue --> DisplayPCs
    
    SelectDuration --> DurationOptions{Choose Duration}
    DurationOptions -->|30 min| SetDuration30[Set 30 minutes]
    DurationOptions -->|1 hour| SetDuration60[Set 60 minutes]
    DurationOptions -->|2 hours| SetDuration120[Set 120 minutes]
    DurationOptions -->|Custom| SetCustom[Set Custom Duration]
    
    SetDuration30 --> ConfirmBooking[Confirm Booking]
    SetDuration60 --> ConfirmBooking
    SetDuration120 --> ConfirmBooking
    SetCustom --> ConfirmBooking
    
    ConfirmBooking --> ValidateBooking{Validate Booking}
    ValidateBooking -->|PC Unavailable| BookingError[Show Error]
    BookingError --> DisplayPCs
    
    ValidateBooking -->|Valid| CreateBooking[Create Booking Record]
    CreateBooking --> ReservePC[Mark PC as Reserved]
    ReservePC --> UpdateStatus[Set PC booking_status = 'in_use']
    UpdateStatus --> CalculateEndTime[Calculate End Time]
    CalculateEndTime --> SaveBooking[Save Booking with Status 'confirmed']
    
    SaveBooking --> Success[Booking Confirmed!]
    Success --> ShowDetails[Show Booking Details:<br/>- PC Name<br/>- Start Time<br/>- End Time<br/>- Duration]
    ShowDetails --> UsePC[Student Uses PC]
    
    UsePC --> SessionWarning{5 Minutes Left?}
    SessionWarning -->|Yes| SendWarning[Send WebSocket Warning]
    SendWarning --> SessionWarning
    SessionWarning -->|No| CheckExpiry{Session Expired?}
    
    CheckExpiry -->|No| UsePC
    CheckExpiry -->|Yes| AutoEnd[Auto End Session]
    AutoEnd --> FreePC[Mark PC as Available]
    FreePC --> UpdateBooking[Set Booking expiry = end_time]
    UpdateBooking --> End([Session Ended])
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style BookingError fill:#ffcdd2
    style ShowRepair fill:#ffcdd2
    style ShowOffline fill:#ffcdd2
    style Success fill:#c8e6c9
```

## Process Steps:

1. **View Available PCs**
   - Student sees available PC count on home page
   - Clicks to view reservation page

2. **Select PC**
   - Views grid of available PCs
   - Selects an available PC
   - System validates PC status

3. **Set Duration**
   - Choose from preset durations or custom
   - Confirm booking

4. **Booking Creation**
   - System creates Booking record
   - Marks PC as 'in_use'
   - Calculates end time based on duration

5. **Session Management**
   - Student uses PC
   - System sends warning 5 minutes before expiry
   - Auto-ends session when time expires
   - Frees PC for next user

