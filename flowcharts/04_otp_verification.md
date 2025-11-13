# OTP Verification Flow

```mermaid
flowchart TD
    Start([User Registration Submitted]) --> GenerateOTP[Generate 6-Digit OTP]
    GenerateOTP --> CreateToken[Create OAuthToken Record]
    CreateToken --> SetExpiry[Set Expiry: 10 minutes]
    SetExpiry --> StoreOTP[Store OTP in Database:<br/>- otp_code<br/>- user_email<br/>- is_active = True<br/>- expires_at]
    
    StoreOTP --> RenderEmail[Render Email Template]
    RenderEmail --> SendEmail[Send OTP Email]
    SendEmail --> EmailSent{Email Sent?}
    
    EmailSent -->|Success| ShowVerifyPage[Show OTP Verification Page]
    EmailSent -->|Failure| LogError[Log Error]
    LogError --> ShowVerifyPage
    
    ShowVerifyPage --> UserEntersOTP[User Enters OTP Code]
    UserEntersOTP --> SubmitOTP[Submit OTP]
    
    SubmitOTP --> ValidateInput{Input Valid?}
    ValidateInput -->|No| ShowError[Show Input Error]
    ShowError --> UserEntersOTP
    
    ValidateInput -->|Yes| QueryToken[Query OAuthToken:<br/>- otp_code matches<br/>- user_email matches<br/>- is_active = True]
    QueryToken --> TokenFound{Token Found?}
    
    TokenFound -->|No| InvalidOTP[Show 'Invalid OTP' Error]
    InvalidOTP --> ResendOption{Resend OTP?}
    ResendOption -->|Yes| GenerateOTP
    ResendOption -->|No| UserEntersOTP
    
    TokenFound -->|Yes| CheckExpiry[Check if OTP Expired]
    CheckExpiry --> IsExpired{Expired?}
    
    IsExpired -->|Yes| ExpiredOTP[Show 'OTP Expired' Error]
    ExpiredOTP --> ResendOption
    
    IsExpired -->|No| DeactivateOTP[Set is_active = False]
    DeactivateOTP --> VerifySuccess[OTP Verified Successfully]
    VerifySuccess --> CreateAccount[Create User Account]
    CreateAccount --> End([Account Created])
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style InvalidOTP fill:#ffcdd2
    style ExpiredOTP fill:#ffcdd2
    style VerifySuccess fill:#c8e6c9
```

## Process Steps:

1. **OTP Generation**
   - System generates random 6-digit code
   - Creates OAuthToken record
   - Sets 10-minute expiry

2. **Email Sending**
   - Renders email template with OTP
   - Sends to user's email address
   - Handles email failures gracefully

3. **OTP Verification**
   - User enters OTP code
   - System queries database
   - Validates code, email, and expiry
   - Deactivates OTP after successful verification

4. **Error Handling**
   - Invalid OTP: Code doesn't match
   - Expired OTP: Past 10-minute window
   - Option to resend OTP

