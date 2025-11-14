# PCheck User Guide

**PCheck** | **User Guide**

---

## INTRODUCTION

Welcome to PCheck, your smart PC reservation and monitoring system!

This web-based application helps students and faculty at Palawan State University's ICT Building to efficiently locate, reserve, and manage computer resources. PCheck provides real-time PC availability information, streamlined booking processes, and comprehensive administrative tools to optimize computer lab usage and reduce waiting times.

---

## SYSTEM OVERVIEW

The PCheck web-based application provides the following core functions:

- **User Authentication** - Protects user accounts and data with secure login options including email/password and Google OAuth.
- **Real-Time PC Availability** - Helps users view current PC status (available, in use, or in queue) in real-time.
- **PC Reservation System** - Lets users reserve available PCs with QR code or Key code validation for secure access.
- **Faculty Block Reservations** - Allows faculty members to reserve up to 30 PCs for class sessions with class list upload.
- **Session Management** - Automatic session timers with extension options and notification alerts.
- **Administrative Dashboard** - Provides staff with tools to manage reservations, monitor usage, and view analytics.
- **Analytics and Reporting** - Tracks usage patterns, peak hours, and generates exportable reports.
- **Chat/Messaging System** - Enables real-time communication between users and staff.
- **Violation Tracking** - Records and manages user violations with suspension capabilities.
- **Role-Based Dashboards** - Has separate interfaces for students, faculty, and staff/admin.

---

## HOW TO ACCESS OR USE THE APP?

1. Open your web browser and navigate to the PCheck application URL (provided by your institution).
2. Registered users can log in using their email and password, or sign in with Google.
3. New users can create an account by providing the required information and completing email verification.
4. Passwords are encrypted to protect user data, and the system uses secure authentication protocols.

---

## LOG IN / SIGN UP (AS USER)

### Login as Student/Faculty
- Access your account using registered credentials (email and password).
- Alternatively, use "Sign in with Google" for quick authentication.

### Email Verification (OTP)
- After registration, a one-time password (OTP) is sent to your registered email address.
- Enter the received OTP to verify your account.
- Resend OTP if the previous one is not received or has expired.

### Profile Completion
- After successful login, complete your profile by selecting:
  - Your role (Student, Faculty, or Staff)
  - Your college/department
  - Additional details such as course, year, and block (for students)
- Profile completion is required before accessing the main application features.

### Navigate to Dashboard
- After completing registration and profile setup, you are redirected to the appropriate dashboard based on your role:
  - **Students/Faculty** → Home page with PC availability
  - **Staff** → Administrative dashboard

---

## USER MANUAL (STUDENT/FACULTY)

### Student/Faculty Dashboard

**PC Availability View:**
- **Real-Time Status** - View current availability of all PCs in the ICT Building.
- **PC List** - Displays all computers with their current status (Available, In Queue, In Use, or Maintenance).
- **Status Indicators** - Color-coded indicators show PC availability at a glance.
- **Search and Filter** - Search for specific PCs or filter by status.

**Reserve a PC:**
- **Select PC** - Click on an available PC from the list.
- **Set Duration** - Choose your desired session duration.
- **Create Reservation** - Submit your reservation request.
- **QR/Key Code** - Receive a QR code or Key code after staff approval.
- **Scan at Lab** - Use the QR code or enter the Key code at the PC to start your session.

**My Reservations:**
- **Active Bookings** - View your current and upcoming reservations.
- **Booking Status** - Check if your reservation is pending, approved, or confirmed.
- **Session Timer** - Monitor remaining time for active sessions.
- **Extend Session** - Request to extend your current session if needed.
- **Cancel Reservation** - Cancel a reservation if your plans change.

**Faculty Block Reservations:**
- **Create Block Booking** - Reserve multiple PCs (up to 30) for class sessions.
- **Upload Class List** - Upload a CSV file with student email addresses.
- **Set Schedule** - Specify start and end times for the class session.
- **Await Approval** - Wait for staff approval before the reservation is activated.
- **View Status** - Check the approval status of your block reservations.

### User Profile

**Profile Information:**
- **Account Details** - View and edit your personal information.
- **College/Course** - View your academic affiliation.
- **Profile Picture** - Upload or update your profile picture.

**Settings:**
- **Change Password** - Update your account password.
- **Edit Profile** - Modify your personal and academic information.
- **Log Out** - Securely sign out of your account.

### Chat/Messaging

**Message List:**
- **Conversations** - View all your conversations with staff members.
- **Unread Messages** - See the count of unread messages.

**Chat Interface:**
- **Send Messages** - Communicate with staff regarding reservations or inquiries.
- **Real-Time Updates** - Receive instant message notifications.
- **Message History** - View past conversations.

---

## FACULTY MANUAL

### Faculty Dashboard

**Block Reservation Management:**
- **Create Block Booking** - Reserve multiple PCs for class sessions.
- **My Block Reservations** - View all your submitted block reservation requests.
- **Reservation Status** - Check approval status (Pending, Confirmed, or Declined).
- **Class List Upload** - Upload CSV file with student corporate email addresses.
- **Reservation Details** - View complete information about each block reservation.

**Block Reservation Process:**
1. **Fill Reservation Form:**
   - Select college and course
   - Enter block/class name
   - Set start and end date/time
   - Specify number of PCs needed (up to 30)
   - Upload class list (CSV format)

2. **Submit for Approval:**
   - Review all information
   - Submit reservation request
   - Wait for staff approval

3. **After Approval:**
   - Receive confirmation notification
   - Access QR codes for approved reservations
   - Share QR codes with students for class session

**View Bookings:**
- **Active Reservations** - See all confirmed block reservations.
- **Past Reservations** - Review completed class sessions.
- **Cancelled Reservations** - View any declined or cancelled bookings.

---

## STAFF/ADMIN GUIDE

### Staff Dashboard

**Main Dashboard:**
- **Analytics Overview** - View key metrics and statistics:
  - Total active sessions
  - Average session duration
  - Peak usage hours
  - College and department breakdown
  - Successful vs. canceled bookings

**PC Management:**
- **PC List** - View all computers in the ICT Building.
- **Add PC** - Register new computers to the system.
- **Edit PC** - Update PC information (name, IP address, status).
- **Delete PC** - Remove PCs from the system.
- **PC Status** - Monitor connection status (Connected/Disconnected).
- **System Condition** - Mark PCs as Active or under Repair.
- **Booking Status** - View current booking status of each PC.

**Reservation Management:**
- **Pending Reservations** - Review and approve/decline student reservation requests.
- **Active Sessions** - Monitor all currently active PC sessions.
- **Booking History** - View all past reservations and bookings.
- **Extend Sessions** - Manually extend user sessions if needed.
- **End Sessions** - Terminate active sessions when necessary.

**Faculty Block Reservations:**
- **Pending Approvals** - Review faculty block reservation requests.
- **Approve/Decline** - Accept or reject block reservation requests.
- **View Details** - Check class list, schedule, and number of PCs requested.
- **Manage Active Block Bookings** - Monitor ongoing class sessions.

**User Management:**
- **User List** - View all registered users (students, faculty, staff).
- **User Details** - Access complete user profiles and information.
- **User Activities** - Monitor user actions and booking history.
- **Violation Management** - View and manage user violations:
  - Create violation records
  - Suspend users for violations
  - Unsuspend users after resolution

**Analytics and Reports:**
- **Usage Statistics** - View detailed usage analytics:
  - Total sessions and duration
  - Peak usage hours
  - College/department breakdown
  - Booking success rates
- **Export Reports** - Generate and download reports (daily, weekly, monthly).
- **Transaction Records** - View all booking transactions and history.

**Chat/Messaging:**
- **Message List** - View all conversations with users.
- **Respond to Inquiries** - Answer user questions and provide support.
- **Mark as Read** - Manage message status.

**Notifications:**
- **System Alerts** - Receive notifications for:
  - New reservation requests
  - Session warnings (approaching time limit)
  - Violation alerts
  - System updates
- **Mark All as Read** - Clear notification indicators.

**Staff Profile:**
- **Staff Information** - View and edit staff account details.
- **Settings** - Configure account preferences.
- **Change Password** - Update staff account password.
- **Log Out** - Securely exit the administrative system.

---

## KEY FEATURES EXPLAINED

### Real-Time PC Monitoring
- PCs are automatically monitored for connection status.
- Status updates in real-time without page refresh.
- Color-coded indicators show availability instantly.

### QR Code/Key Code System
- **QR Code** - Generated after reservation approval, scan at the PC to start session.
- **Key Code** - Alternative authentication method, enter code at PC terminal.
- Both methods ensure secure access and prevent unauthorized PC usage.

### Session Management
- **Automatic Timer** - Sessions are automatically tracked and managed.
- **Extension Option** - Users can request to extend their session if no conflicts.
- **Auto-Cleanup** - Expired sessions are automatically released.
- **Notifications** - Users receive alerts when session time is about to end.

### Violation System
- **Violation Levels** - Minor, Moderate, and Major violations.
- **Automatic Tracking** - System records violations automatically.
- **Suspension** - Staff can suspend users for violations.
- **Resolution** - Violations can be marked as resolved.

### Peripheral Monitoring
- **Device Detection** - System monitors USB and peripheral device connections.
- **Alerts** - Staff receives notifications when devices are attached/removed.
- **Security** - Helps maintain lab security and prevent unauthorized device usage.

---

## TROUBLESHOOTING

### Cannot Log In
- Verify your email and password are correct.
- Check if your account is verified (check email for OTP).
- Try "Forgot Password" if you cannot remember your password.
- Contact staff if issues persist.

### Cannot Reserve PC
- Ensure the PC status shows "Available."
- Check if you have any active violations or suspensions.
- Verify your profile is complete.
- Contact staff for assistance.

### QR Code Not Working
- Ensure the reservation is approved by staff.
- Check if the session time has not expired.
- Try using the Key code alternative.
- Contact staff if the issue continues.

### Session Ended Unexpectedly
- Check if your session time limit was reached.
- Verify if staff manually ended the session.
- Check for any violation records.
- Contact staff for clarification.

### Cannot Access Block Reservation
- Ensure you are logged in as a Faculty account.
- Verify your profile role is set to "Faculty."
- Check if you have reached the maximum PC limit (30).
- Contact staff for assistance.

---

## CONTACT AND SUPPORT

For technical support or inquiries:
- Use the Chat/Messaging feature to contact staff directly.
- Visit the ICT Building for in-person assistance.
- Check system notifications for important updates.

---

## SECURITY NOTES

- Never share your login credentials with others.
- Keep your QR codes and Key codes confidential.
- Log out when finished, especially on shared computers.
- Report any suspicious activity to staff immediately.
- The system uses encrypted connections to protect your data.

---

**PCheck - Optimizing ICT Lab Resources for Palawan State University**

*Version 1.0 | Last Updated: 2025*

