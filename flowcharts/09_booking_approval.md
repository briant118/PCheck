# Student Booking Approval Flow (Staff)

```mermaid
flowchart TD
    Start([Staff Views Bookings]) --> BookingList[Bookings List Page]
    BookingList --> FilterBookings{Filter Bookings}
    
    FilterBookings -->|Pending| ViewPending[View Pending Bookings]
    FilterBookings -->|Approved| ViewApproved[View Approved Bookings]
    FilterBookings -->|All| ViewAll[View All Bookings]
    
    ViewPending --> SelectBooking[Select Booking to Review]
    ViewApproved --> SelectBooking
    ViewAll --> SelectBooking
    
    SelectBooking --> ClickReview[Click 'Review' Button]
    ClickReview --> BookingDetails[Show Booking Details:<br/>- User Name, ID<br/>- Course, Year, Block<br/>- PC Name<br/>- Start Time, Duration<br/>- Number of PCs]
    
    BookingDetails --> StaffDecision{Staff Decision?}
    
    StaffDecision -->|Approve| ClickApprove[Click 'Approve' Button]
    StaffDecision -->|Decline| ClickDecline[Click 'Decline' Button]
    StaffDecision -->|Cancel| BookingList
    
    ClickApprove --> ValidateBooking{Booking Still Valid?}
    ValidateBooking -->|No| BookingInvalid[Show Error:<br/>Booking No Longer Valid]
    BookingInvalid --> BookingList
    
    ValidateBooking -->|Yes| ApproveBooking[Approve Booking]
    ApproveBooking --> UpdatePC[Call PC.approve Method]
    UpdatePC --> SetInUse[Set PC booking_status = 'in_use']
    SetInUse --> SetStartTime[Set booking.start_time = now]
    SetStartTime --> CalculateEndTime[Calculate booking.end_time<br/>start_time + duration]
    CalculateEndTime --> SetStatus[Set booking.status = 'confirmed']
    SetStatus --> SaveBooking[Save Booking]
    SaveBooking --> ShowSuccess[Show 'Reservation Approved' Message]
    ShowSuccess --> BookingList
    
    ClickDecline --> ConfirmDecline{Confirm Decline?}
    ConfirmDecline -->|No| BookingDetails
    ConfirmDecline -->|Yes| DeclineBooking[Decline Booking]
    DeclineBooking --> FreePC[Set PC booking_status = 'available']
    FreePC --> SetStatusDeclined[Set booking.status = 'cancelled']
    SetStatusDeclined --> SaveDeclined[Save Booking]
    SaveDeclined --> ShowDeclined[Show 'Reservation Declined' Message]
    ShowDeclined --> BookingList
    
    AutoApprove[Auto-Approval via QR Scan] --> QRScan[QR Code Scanned]
    QRScan --> ValidateQR{QR Valid?}
    ValidateQR -->|No| InvalidQR[Show Error]
    ValidateQR -->|Yes| AutoApproveBooking[Auto-Approve Booking]
    AutoApproveBooking --> UpdatePC
    InvalidQR --> End([End])
    
    BookingList --> End
    ShowSuccess --> End
    ShowDeclined --> End
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style BookingInvalid fill:#ffcdd2
    style InvalidQR fill:#ffcdd2
    style ShowSuccess fill:#c8e6c9
    style ShowDeclined fill:#fff9c4
```

## Process Steps:

1. **View Bookings**
   - Staff accesses bookings page
   - Can filter by status (pending, approved, all)
   - Views list of bookings

2. **Review Booking**
   - Staff clicks 'Review' on a booking
   - System displays full booking details
   - Shows user info, PC info, timing

3. **Approve Booking**
   - Staff clicks 'Approve'
   - System validates booking is still valid
   - Marks PC as 'in_use'
   - Sets start time and calculates end time
   - Sets status to 'confirmed'
   - Shows success message

4. **Decline Booking**
   - Staff clicks 'Decline'
   - Confirms action
   - Frees PC (sets to 'available')
   - Sets booking status to 'cancelled'
   - Shows decline message

5. **Auto-Approval**
   - QR code scan can auto-approve
   - Validates QR code
   - Automatically approves booking
   - Redirects to dashboard

