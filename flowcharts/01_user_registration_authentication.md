# User Registration & Authentication Flow

```mermaid
flowchart TD
    Start([User Visits Site]) --> LoginPage{Already Registered?}
    
    LoginPage -->|No| Register[Registration Page]
    LoginPage -->|Yes| Login[Login Page]
    
    Register --> FillForm[Fill Registration Form:<br/>- Role Student/Faculty<br/>- Name, Email<br/>- College, Course, Year, Block]
    FillForm --> SubmitReg[Submit Registration]
    SubmitReg --> CreatePending[Create PendingUser Record]
    CreatePending --> SendOTP[Send OTP Code via Email]
    SendOTP --> VerifyPage[OTP Verification Page]
    
    VerifyPage --> EnterOTP[Enter OTP Code]
    EnterOTP --> ValidateOTP{OTP Valid?}
    ValidateOTP -->|No| InvalidOTP[Show Error]
    InvalidOTP --> ResendOTP{Resend OTP?}
    ResendOTP -->|Yes| SendOTP
    ResendOTP -->|No| EnterOTP
    
    ValidateOTP -->|Yes| CreateUser[Create User Account]
    CreateUser --> CreateProfile[Create Profile with Role]
    CreateProfile --> DeletePending[Delete PendingUser]
    DeletePending --> CompleteProfile{Profile Complete?}
    
    CompleteProfile -->|No| ProfileForm[Complete Profile Form]
    ProfileForm --> SaveProfile[Save Profile]
    SaveProfile --> Redirect
    
    CompleteProfile -->|Yes| Redirect{User Role?}
    
    Login --> EnterCredentials[Enter Email/Password]
    EnterCredentials --> Auth{Authenticate}
    Auth -->|Invalid| LoginError[Show Error]
    LoginError --> EnterCredentials
    Auth -->|Valid| CheckProfile{Has Profile?}
    
    CheckProfile -->|No| CompleteProfile
    CheckProfile -->|Yes| CheckRole{Profile Role?}
    
    CheckRole -->|No Role| CompleteProfile
    CheckRole -->|Student| StudentHome[Student Home Page]
    CheckRole -->|Faculty| FacultyHome[Faculty Home Page]
    CheckRole -->|Staff| StaffDashboard[Staff Dashboard]
    
    Redirect -->|Student| StudentHome
    Redirect -->|Faculty| FacultyHome
    Redirect -->|Staff| StaffDashboard
    
    StudentHome --> End([Access Granted])
    FacultyHome --> End
    StaffDashboard --> End
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style InvalidOTP fill:#ffcdd2
    style LoginError fill:#ffcdd2
```

## Process Steps:

1. **Registration**
   - User fills registration form with role, personal info, college details
   - System creates PendingUser record
   - OTP code sent to email
   - User verifies OTP
   - User account and profile created
   - PendingUser deleted

2. **Login**
   - User enters credentials
   - System authenticates
   - Checks for profile completion
   - Redirects based on role

3. **Profile Completion**
   - Required if profile incomplete or missing role
   - User selects role and completes details
   - Redirects to appropriate home page

