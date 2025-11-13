# Database ERD Documentation

This folder contains the Entity Relationship Diagram (ERD) for the PCheck system database.

## Files

- **[database_erd.md](database_erd.md)** - Complete ERD with all entities, relationships, and detailed descriptions

## Database Overview

The PCheck system uses a Django-based database with the following main entity groups:

### 1. User Management
- **User** (Django Auth) - Core authentication
- **Profile** - Extended user information
- **PendingUser** - Temporary registration data

### 2. Academic Structure
- **College** - Academic departments
- **Course** - Academic programs

### 3. PC Management
- **PC** - Computer/lab machines
- **PeripheralEvent** - USB device monitoring

### 4. Booking System
- **Booking** - Individual PC bookings
- **FacultyBooking** - Bulk class bookings

### 5. Communication
- **ChatRoom** - Conversation containers
- **Chat** - Individual messages

### 6. Violations
- **Violation** - User violation records

## How to View the ERD

The ERD is written in **Mermaid** syntax. You can view it:

1. **GitHub/GitLab**: Renders automatically in markdown
2. **VS Code**: Install "Markdown Preview Mermaid Support" extension
3. **Online**: Copy Mermaid code to [Mermaid Live Editor](https://mermaid.live/)
4. **Documentation Tools**: Most platforms support Mermaid ERD diagrams

## Database Relationships Summary

### One-to-One
- User ↔ Profile

### One-to-Many
- User → Bookings
- User → FacultyBookings
- User → Violations
- College → Courses
- College → Profiles
- PC → Bookings
- PC → PeripheralEvents
- FacultyBooking → Bookings
- ChatRoom → Chats

### Many-to-One
- Profile → User
- Profile → College
- Course → College
- Booking → User
- Booking → PC
- Booking → FacultyBooking
- Violation → User
- Violation → PC
- Chat → ChatRoom
- Chat → User (sender/recipient)

## Key Features

- **Flexible Relationships**: Many foreign keys are nullable for flexibility
- **Cascade Deletes**: Most relationships use CASCADE to maintain data integrity
- **Status Tracking**: Multiple entities track status (booking_status, violation status, chat status)
- **Audit Fields**: Created_at, updated_at, timestamp fields for tracking
- **File Storage**: Profile pictures and booking attachments stored in media

## Database Design Principles

1. **Normalization**: Entities are properly normalized
2. **Referential Integrity**: Foreign keys ensure data consistency
3. **Soft Deletes**: Some entities use status fields instead of hard deletes
4. **Audit Trail**: Timestamps track when records are created/updated
5. **Flexibility**: Nullable fields allow for optional data

