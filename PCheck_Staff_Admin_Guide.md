# PCheck Staff/Admin Guide

**PCheck** | **Staff/Admin Guide**

---

## STAFF/ADMIN MANUAL

### MAIN DASHBOARD

**Analytics Overview:**
- **Total Sessions** - View the total number of active and completed sessions.
- **Average Duration** - See the average session length across all users.
- **Peak Usage Hours** - Identify busiest times of day for resource planning.
- **College Breakdown** - View usage statistics by college/department.
- **Booking Statistics** - Monitor successful vs. canceled bookings.
- **Real-Time Metrics** - All analytics update in real-time.

**Quick Actions:**
- **Pending Reservations** - Quick access to reservation approvals.
- **Active Sessions** - View all currently active PC sessions.
- **System Alerts** - See important notifications and warnings.

---

### PC MANAGEMENT PAGE

**Interface Sections:**
- **All PCs Tab** - Displays all computers registered in the system.
- **Search PC** - Quickly search for a specific PC by name or IP address.
- **Status Filter** - Filter PCs by status (Available, In Use, In Queue, Maintenance).
- **Connection Status** - View real-time connection status (Connected/Disconnected).

**Table Columns:**
- **PC Name** - Computer identifier/name.
- **IP Address** - Network IP address of the PC.
- **Connection Status** - Current network connection state.
- **System Condition** - Active or Repair status.
- **Booking Status** - Current reservation status.
- **Actions** - Available management options.

**Actions Available:**
- **View Details** - Display complete PC information and booking history.
- **Edit PC** - Update PC name, IP address, or status.
- **Ping IP** - Test network connectivity to the PC.
- **Delete PC** - Remove PC from the system (use with caution).

**Add New PC:**
- Click "Add PC" button.
- Enter PC name (must be unique).
- Enter IP address.
- Set initial status and system condition.
- Save to register the PC in the system.

**Update PC Status:**
- **Mark as Active** - PC is operational and available for booking.
- **Mark as Repair** - PC is under maintenance and unavailable.
- **Update Connection** - Manually update connection status if needed.

---

### RESERVATION MANAGEMENT PAGE

**Interface Sections:**
- **Pending Reservations Tab** - Shows all reservation requests awaiting approval.
- **Active Sessions Tab** - Displays all currently active PC sessions.
- **Booking History Tab** - View all past reservations and bookings.
- **Search Bar** - Search reservations by user name, PC name, or booking ID.
- **Date Filter** - Filter reservations by date range.

**Pending Reservations:**
- **Table Columns:**
  - **User** - Name of the user requesting reservation.
  - **PC** - Computer being reserved.
  - **Duration** - Requested session length.
  - **Start Time** - Requested session start time.
  - **Status** - Current approval status.
  - **Actions** - Approve or Decline buttons.

- **Actions Available:**
  - **Approve** - Accept the reservation request and generate QR/Key code.
  - **Decline** - Reject the reservation request with optional reason.

**Active Sessions:**
- **Table Columns:**
  - **User** - Name of the active user.
  - **PC** - Computer currently in use.
  - **Start Time** - Session start timestamp.
  - **End Time** - Scheduled session end time.
  - **Remaining Time** - Time left in session.
  - **Actions** - Extend or End session options.

- **Actions Available:**
  - **Extend Session** - Add additional time to the current session.
  - **End Session** - Manually terminate the session early.
  - **View Details** - See complete session information.

**Booking History:**
- View all completed, canceled, and expired bookings.
- Filter by date range, user, or PC.
- Export booking data for reporting purposes.

---

### FACULTY BLOCK RESERVATION PAGE

**Interface Sections:**
- **Pending Approvals Tab** - Shows faculty block reservation requests.
- **Approved Reservations Tab** - Displays confirmed block bookings.
- **Search Bar** - Search by faculty name, course, or college.
- **Date Filter** - Filter by reservation date range.

**Table Columns:**
- **Faculty** - Name of the requesting faculty member.
- **College** - Academic department.
- **Course** - Course name or code.
- **Block** - Class section identifier.
- **Number of PCs** - Total PCs requested (up to 30).
- **Start Date/Time** - Class session start.
- **End Date/Time** - Class session end.
- **Status** - Approval status (Pending, Confirmed, Declined).
- **Actions** - Approve or Decline buttons.

**Actions Available:**
- **View Details** - Display complete reservation information including class list.
- **Approve** - Confirm the block reservation and activate it.
- **Decline** - Reject the reservation request.

**Review Process:**
1. Check faculty information and credentials.
2. Verify class list and student email addresses.
3. Confirm PC availability for requested time slot.
4. Review number of PCs requested (must not exceed 30).
5. Approve or decline based on availability and validity.

---

### USER MANAGEMENT PAGE

**Interface Sections:**
- **All Users Tab** - Shows all registered user profiles.
- **Search Bar** - Search users by name, email, or school ID.
- **Role Filter** - Filter by user role (Student, Faculty, Staff).
- **College Filter** - Filter by college/department.
- **Date Range Filter** - Display users registered within a specific timeframe.

**Table Columns:**
- **User ID** - Unique user identifier.
- **Name** - Full name of the user.
- **Email** - Registered email address.
- **Role** - User role (Student, Faculty, Staff).
- **College** - Academic department.
- **School ID** - Student or faculty ID number.
- **Date Registered** - Account creation date.
- **Last Login** - Most recent login timestamp.
- **Status** - Account status (Active, Suspended).
- **Actions** - Available management options.

**Actions Available:**
- **View Profile** - Display complete user profile and information.
- **View Activities** - See user's booking history and actions.
- **Suspend User** - Temporarily disable user account (for violations).
- **Unsuspend User** - Reactivate a suspended account.
- **Edit Profile** - Modify user information (staff only).

---

### USER ACTIVITIES PAGE

**Interface Sections:**
- **All Activities Tab** - Displays all user actions and bookings.
- **Search Bar** - Search activities by user name or action type.
- **User Filter** - Filter activities by specific user.
- **Date Range Filter** - View activities within a specific period.
- **Activity Type Filter** - Filter by action type (Booking, Login, etc.).

**Table Columns:**
- **User** - Name of the user who performed the action.
- **Action** - Type of activity (e.g., "Created Booking", "Extended Session").
- **PC** - Computer involved (if applicable).
- **Timestamp** - Date and time of the activity.
- **Details** - Additional information about the action.

**Usage:**
- Monitor user behavior and system usage patterns.
- Track booking patterns and identify issues.
- Generate activity reports for administrative purposes.

---

### VIOLATION MANAGEMENT

**Interface Sections:**
- **All Violations Tab** - Shows all recorded violations.
- **Search Bar** - Search violations by user name or violation type.
- **Status Filter** - Filter by violation status (Active, Resolved).
- **Level Filter** - Filter by violation level (Minor, Moderate, Major).

**Table Columns:**
- **User** - Name of the user with violation.
- **PC** - Computer involved (if applicable).
- **Violation Level** - Severity (Minor, Moderate, Major).
- **Reason** - Description of the violation.
- **Date** - Violation timestamp.
- **Status** - Current status (Active, Resolved, Suspended).
- **Actions** - Available management options.

**Actions Available:**
- **View Details** - Display complete violation information.
- **Suspend User** - Temporarily disable user account due to violation.
- **Unsuspend User** - Reactivate account after violation resolution.
- **Mark as Resolved** - Close violation record after resolution.

**Creating Violations:**
- Click "Create Violation" button.
- Select user from the list.
- Choose violation level.
- Enter violation reason/description.
- Optionally select PC involved.
- Save to record the violation.

---

### ANALYTICS AND REPORTS PAGE

**Interface Sections:**
- **Usage Statistics** - View comprehensive usage analytics.
- **Reports Generator** - Create and export reports.
- **Date Range Selector** - Choose reporting period.
- **Export Options** - Download reports in various formats.

**Analytics Available:**
- **Total Sessions** - Count of all completed sessions.
- **Average Session Duration** - Mean session length.
- **Peak Usage Hours** - Busiest time periods.
- **College Breakdown** - Usage by academic department.
- **Course Breakdown** - Usage by course/program.
- **Booking Success Rate** - Percentage of successful bookings.
- **Cancellation Rate** - Percentage of canceled reservations.
- **PC Utilization** - Usage statistics per computer.

**Report Generation:**
- **Daily Reports** - Generate reports for a specific day.
- **Weekly Reports** - Create weekly usage summaries.
- **Monthly Reports** - Generate monthly analytics.
- **Custom Range** - Create reports for any date range.
- **Export Formats** - Download as CSV, PDF, or Excel.

**Report Contents:**
- Session summaries and statistics.
- User activity breakdowns.
- PC utilization data.
- Booking trends and patterns.
- Violation records (if applicable).

---

### CHAT/MESSAGING PAGE

**Interface Sections:**
- **Message List** - Displays all conversations with users.
- **Unread Count** - Shows number of unread messages.
- **Search Conversations** - Find specific user conversations.
- **Active Conversations** - Highlight ongoing chats.

**Chat Interface:**
- **Conversation View** - Display message history with a user.
- **Send Messages** - Respond to user inquiries.
- **Real-Time Updates** - Receive instant message notifications.
- **Mark as Read** - Update message status.
- **Mark All as Read** - Clear all unread indicators.

**Message Management:**
- View all messages from users.
- Respond to inquiries and provide support.
- Track conversation history.
- Manage message status and notifications.

---

### NOTIFICATIONS PAGE

**Interface Sections:**
- **All Notifications Tab** - Shows all system alerts and updates.
- **Unread Notifications** - Highlights new notifications.
- **Notification Types** - Filter by notification category.
- **Date Filter** - View notifications by date range.

**Notification Types:**
- **Reservation Requests** - New booking requests requiring approval.
- **Session Warnings** - Alerts for sessions approaching time limit.
- **Violation Alerts** - Notifications about user violations.
- **System Updates** - Important system announcements.
- **Block Reservation Requests** - Faculty block booking approvals needed.

**Actions Available:**
- **View Details** - See complete notification information.
- **Mark as Read** - Clear individual notification.
- **Mark All as Read** - Clear all notification indicators.
- **Take Action** - Direct links to relevant pages (e.g., approve reservation).

---

### STAFF PROFILE PAGE

**Profile Information:**
- **Staff Details** - View and edit staff account information.
- **Account Settings** - Configure account preferences.
- **Change Password** - Update staff account password.
- **Email Settings** - Manage email notifications.

**Account Management:**
- **Update Information** - Modify staff profile details.
- **Security Settings** - Configure account security options.
- **Notification Preferences** - Set notification preferences.
- **Log Out** - Securely exit the administrative system.

---

## KEY ADMINISTRATIVE FUNCTIONS

### Approving Reservations
1. Navigate to Reservation Management → Pending Reservations.
2. Review reservation details (user, PC, duration, time).
3. Check PC availability and user account status.
4. Click "Approve" to confirm or "Decline" to reject.
5. System automatically generates QR/Key code upon approval.

### Managing Active Sessions
1. Go to Reservation Management → Active Sessions.
2. View all currently active PC sessions.
3. Monitor remaining time for each session.
4. Extend sessions if needed or end sessions early if necessary.
5. System sends notifications to users when sessions are ending.

### Handling Violations
1. Navigate to Violation Management.
2. Create violation records for user infractions.
3. Assign violation levels (Minor, Moderate, Major).
4. Suspend users if necessary based on violation severity.
5. Unsuspend users after violation resolution.

### Generating Reports
1. Go to Analytics and Reports page.
2. Select date range for the report.
3. Choose report type (Daily, Weekly, Monthly, Custom).
4. Review analytics and statistics.
5. Export report in desired format (CSV, PDF, Excel).

### PC Maintenance
1. Navigate to PC Management page.
2. Select PC requiring maintenance.
3. Update system condition to "Repair."
4. PC becomes unavailable for booking.
5. Mark as "Active" when maintenance is complete.

---

## BEST PRACTICES

### Reservation Management
- Review pending reservations promptly to reduce user waiting time.
- Check PC availability before approving reservations.
- Monitor active sessions to ensure fair resource allocation.
- Extend sessions only when appropriate and no conflicts exist.

### User Management
- Regularly review user activities for unusual patterns.
- Address violations promptly and consistently.
- Maintain accurate user profiles and information.
- Monitor suspended accounts and resolve issues timely.

### System Monitoring
- Regularly check PC connection status.
- Monitor system analytics for usage patterns.
- Review violation records and take appropriate actions.
- Generate regular reports for administrative review.

### Communication
- Respond to user messages promptly.
- Provide clear explanations for declined reservations.
- Notify users of important system updates.
- Maintain professional communication in all interactions.

---

## TROUBLESHOOTING FOR STAFF

### Cannot Access Dashboard
- Verify staff account credentials.
- Check if account has staff/admin privileges.
- Contact system administrator if issues persist.

### PC Status Not Updating
- Manually ping the PC to check connectivity.
- Verify network connection.
- Update PC status manually if needed.

### Reservation Approval Issues
- Check if PC is actually available.
- Verify user account is active and not suspended.
- Review booking conflicts and time overlaps.
- Contact technical support if system errors occur.

### Report Generation Errors
- Verify date range is valid.
- Check if sufficient data exists for the period.
- Try exporting in different format.
- Contact technical support if issue persists.

---

## SECURITY AND PRIVACY

- Never share staff login credentials.
- Log out when finished, especially on shared computers.
- Protect user data and maintain confidentiality.
- Follow institutional privacy policies.
- Report security concerns immediately.

---

**PCheck Staff/Admin Guide**

*Version 1.0 | Last Updated: 2025*

