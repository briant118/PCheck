# PCheck System Flowcharts

This folder contains detailed flowcharts documenting all major processes in the PCheck (PC Check) system.

## Flowchart Files

1. **[User Registration & Authentication](01_user_registration_authentication.md)**
   - User registration process
   - OTP verification
   - Login flow
   - Profile completion
   - Role-based redirection

2. **[Student PC Booking](02_student_pc_booking.md)**
   - Viewing available PCs
   - Selecting a PC
   - Setting booking duration
   - Creating booking
   - Session management and auto-cleanup

3. **[Faculty Bulk Booking](03_faculty_bulk_booking.md)**
   - Multi-step booking form
   - Staff approval process
   - QR code generation
   - Email distribution
   - QR code validation and PC assignment

4. **[OTP Verification](04_otp_verification.md)**
   - OTP generation
   - Email sending
   - OTP validation
   - Error handling and resend

5. **[Violation & Suspension](05_violation_suspension.md)**
   - Violation detection
   - Creating violation records
   - User suspension
   - Unsuspension process

6. **[Session Management](06_session_management.md)**
   - Automatic cleanup middleware
   - Session warning system
   - Manual cleanup
   - Early session termination

7. **[PC Management](07_pc_management.md)**
   - Adding/editing/deleting PCs
   - PC status monitoring
   - Ping functionality
   - Connection status updates

8. **[Chat/Messaging System](08_chat_messaging.md)**
   - Real-time messaging via WebSocket
   - Role-based messaging rules
   - Conversation management
   - Message status tracking

9. **[Booking Approval](09_booking_approval.md)**
   - Staff review of student bookings
   - Approve/decline workflow
   - Auto-approval via QR scan
   - Booking status management

10. **[Peripheral Monitoring](10_peripheral_monitoring.md)**
    - USB/peripheral device detection
    - Real-time monitoring script
    - Staff alerting system
    - Device attachment/removal tracking

11. **[Profile Management](11_profile_management.md)**
    - Profile viewing and editing
    - Profile picture upload
    - Password change/set
    - Form validation

12. **[Google OAuth Login](12_google_oauth_login.md)**
    - Google authentication flow
    - Account linking
    - School ID extraction
    - Profile completion for OAuth users

## How to View Flowcharts

These flowcharts are written in **Mermaid** syntax. You can view them:

1. **GitHub/GitLab**: Flowcharts render automatically in markdown files
2. **VS Code**: Install "Markdown Preview Mermaid Support" extension
3. **Online**: Copy Mermaid code to [Mermaid Live Editor](https://mermaid.live/)
4. **Documentation Tools**: Most modern documentation platforms support Mermaid

## Flowchart Conventions

- **Start nodes** (blue): Beginning of process
- **End nodes** (green): Successful completion
- **Error nodes** (red): Error states or failures
- **Decision diamonds**: Decision points with yes/no branches
- **Process rectangles**: Actions or steps in the process

## System Overview

The PCheck system manages PC reservations for Palawan State University, supporting:
- **Students**: Individual PC bookings with duration selection
- **Faculty**: Bulk class bookings with QR code access
- **Staff**: System management, monitoring, and approval workflows

All processes include proper error handling, validation, and user feedback mechanisms.

