# PC Management Flow (Staff)

```mermaid
flowchart TD
    Start([Staff Logs In]) --> Dashboard[Staff Dashboard]
    Dashboard --> PCLink[Click 'PCs' in Sidebar]
    PCLink --> PCList[PC List Page]
    
    PCList --> ViewPCs[View All PCs:<br/>- Name<br/>- Status Connected/Disconnected<br/>- Booking Status<br/>- System Condition]
    
    ViewPCs --> Actions{Action?}
    
    Actions -->|Add PC| AddPC[Add New PC]
    Actions -->|Edit PC| EditPC[Edit Existing PC]
    Actions -->|Delete PC| DeletePC[Delete PC]
    Actions -->|Ping PC| PingPC[Ping PC IP]
    Actions -->|View Details| ViewDetails[View PC Details]
    
    AddPC --> FillPCForm[Fill PC Form:<br/>- Name<br/>- IP Address<br/>- MAC Address optional]
    FillPCForm --> SavePC[Save PC]
    SavePC --> CreatePC[Create PC Record:<br/>- status = 'disconnected'<br/>- booking_status = 'available'<br/>- system_condition = 'active']
    CreatePC --> SuccessAdd[PC Added Successfully]
    SuccessAdd --> PCList
    
    EditPC --> SelectPC[Select PC to Edit]
    SelectPC --> LoadPCData[Load PC Data]
    LoadPCData --> EditForm[Edit PC Details]
    EditForm --> UpdatePC[Update PC Record]
    UpdatePC --> SuccessEdit[PC Updated Successfully]
    SuccessEdit --> PCList
    
    DeletePC --> SelectPCDelete[Select PC to Delete]
    SelectPCDelete --> ConfirmDelete{Confirm Delete?}
    ConfirmDelete -->|No| PCList
    ConfirmDelete -->|Yes| CheckBookings{Has Active Bookings?}
    
    CheckBookings -->|Yes| CannotDelete[Show Error:<br/>Cannot delete PC with active bookings]
    CannotDelete --> PCList
    CheckBookings -->|No| DeleteRecord[Delete PC Record]
    DeleteRecord --> SuccessDelete[PC Deleted Successfully]
    SuccessDelete --> PCList
    
    PingPC --> SelectPCPing[Select PC to Ping]
    SelectPCPing --> SendPing[Send ICMP Ping Request]
    SendPing --> PingResult{Ping Successful?}
    
    PingResult -->|Yes| UpdateConnected[Update PC status = 'connected']
    PingResult -->|No| UpdateDisconnected[Update PC status = 'disconnected']
    
    UpdateConnected --> ShowResult[Show Ping Result]
    UpdateDisconnected --> ShowResult
    ShowResult --> PCList
    
    ViewDetails --> SelectPCView[Select PC]
    SelectPCView --> ShowDetails[Show PC Details:<br/>- All PC Info<br/>- Booking History<br/>- Violations<br/>- Status Log]
    ShowDetails --> PCList
    
    MonitorStatus[Background: Monitor PC Status] --> CheckConnection[Periodically Check Connection]
    CheckConnection --> PingAll[Ping All PCs]
    PingAll --> UpdateStatus[Update PC Status Automatically]
    UpdateStatus --> MonitorStatus
    
    style Start fill:#e1f5ff
    style SuccessAdd fill:#c8e6c9
    style SuccessEdit fill:#c8e6c9
    style SuccessDelete fill:#c8e6c9
    style CannotDelete fill:#ffcdd2
    style UpdateConnected fill:#c8e6c9
    style UpdateDisconnected fill:#fff9c4
```

## Process Steps:

1. **View PCs**
   - Staff views list of all PCs
   - Sees current status and booking state
   - Can filter and search

2. **Add PC**
   - Enter PC details (name, IP, MAC)
   - System creates PC record
   - Initial status: disconnected

3. **Edit PC**
   - Select PC to edit
   - Update details
   - Save changes

4. **Delete PC**
   - Select PC to delete
   - System checks for active bookings
   - Cannot delete if bookings exist
   - Confirms and deletes

5. **Ping PC**
   - Test PC connectivity
   - Updates status based on ping result
   - Shows connection status

6. **Monitor Status**
   - Background process pings PCs
   - Automatically updates connection status
   - Keeps status current

