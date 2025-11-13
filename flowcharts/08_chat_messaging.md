# Chat/Messaging System Flow

```mermaid
flowchart TD
    Start([User Accesses Chat]) --> CheckRole{User Role?}
    
    CheckRole -->|Student| StudentChat[Student Chat View]
    CheckRole -->|Faculty| FacultyChat[Faculty Chat View]
    CheckRole -->|Staff| StaffChat[Staff Chat View]
    
    StudentChat --> InitiateChat[Click 'PCheck Support']
    FacultyChat --> InitiateChat
    StaffChat --> SelectRecipient[Select Recipient:<br/>Faculty or Student]
    
    InitiateChat --> CheckExisting{Existing Conversation?}
    SelectRecipient --> CheckExisting
    
    CheckExisting -->|Yes| LoadConversation[Load Existing Conversation]
    CheckExisting -->|No| CreateRoom[Create ChatRoom]
    
    CreateRoom --> ValidateRules{Validate Messaging Rules}
    LoadConversation --> ValidateRules
    
    ValidateRules --> RuleCheck{Check Rules}
    RuleCheck -->|Student/Faculty| CanMessageStaff{Recipient is Staff?}
    RuleCheck -->|Staff| CanMessageUser{Recipient is Student/Faculty?}
    RuleCheck -->|PCheck Support| CanMessageAdmin{Recipient is Staff/Admin?}
    
    CanMessageStaff -->|No| ShowError[Show Error:<br/>Can only message Staff]
    CanMessageUser -->|No| ShowErrorStaff[Show Error:<br/>Can only message Students/Faculty]
    CanMessageAdmin -->|No| ShowErrorSupport[Show Error:<br/>Can only message Staff/Admin]
    
    ShowError --> EndError([Error])
    ShowErrorStaff --> EndError
    ShowErrorSupport --> EndError
    
    CanMessageStaff -->|Yes| SendMessage
    CanMessageUser -->|Yes| SendMessage
    CanMessageAdmin -->|Yes| SendMessage
    
    SendMessage[User Types Message] --> ValidateMessage{Message Valid?}
    ValidateMessage -->|No| ShowValidationError[Show Validation Error]
    ShowValidationError --> SendMessage
    
    ValidateMessage -->|Yes| CreateChat[Create Chat Record:<br/>- room<br/>- sender<br/>- message<br/>- status = 'sent']
    
    CreateChat --> WebSocketSend[Send via WebSocket]
    WebSocketSend --> BroadcastMessage[Broadcast to Recipient]
    BroadcastMessage --> UpdateUnread[Update Unread Count]
    UpdateUnread --> MessageDelivered[Message Delivered]
    
    MessageDelivered --> RealTimeUpdate[Real-time Update via WebSocket]
    RealTimeUpdate --> DisplayMessage[Display in Chat UI]
    DisplayMessage --> MarkRead{Recipient Views?}
    
    MarkRead -->|Yes| UpdateStatus[Update Chat status = 'read']
    MarkRead -->|No| KeepUnread[Keep as Unread]
    
    UpdateStatus --> End([Message Processed])
    KeepUnread --> End
    
    Background[Background: WebSocket Connection] --> ListenMessages[Listen for Messages]
    ListenMessages --> ReceiveMessage[Receive Message]
    ReceiveMessage --> ParseMessage[Parse Message Data]
    ParseMessage --> UpdateUI[Update UI in Real-time]
    UpdateUI --> ListenMessages
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style ShowError fill:#ffcdd2
    style ShowErrorStaff fill:#ffcdd2
    style ShowErrorSupport fill:#ffcdd2
    style MessageDelivered fill:#c8e6c9
```

## Process Steps:

1. **Access Chat**
   - User clicks chat/support link
   - System checks user role
   - Loads appropriate chat interface

2. **Conversation Management**
   - Checks for existing conversation
   - Creates new ChatRoom if needed
   - Links initiator and receiver

3. **Messaging Rules**
   - **Students**: Can only message Staff/Admin
   - **Faculty**: Can only message Staff/Admin
   - **Staff**: Can message Students/Faculty (not other staff)
   - **PCheck Support**: Can message Staff/Admin only

4. **Message Sending**
   - User types and sends message
   - System validates message
   - Creates Chat record
   - Broadcasts via WebSocket

5. **Real-time Updates**
   - WebSocket connection maintains real-time sync
   - Messages appear instantly
   - Unread count updates automatically
   - Status changes (sent → read)

