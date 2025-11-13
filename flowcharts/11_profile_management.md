# Profile Management Flow

```mermaid
flowchart TD
    Start([User Accesses Profile]) --> ViewProfile[View Profile Page]
    ViewProfile --> DisplayInfo[Display Profile Information:<br/>- Name, Email<br/>- College, Course<br/>- Year, Block<br/>- Profile Picture]
    
    DisplayInfo --> ProfileActions{Action?}
    
    ProfileActions -->|Edit Profile| ClickEdit[Click 'Update Profile']
    ProfileActions -->|Change Password| ClickPassword[Click 'Change Password']
    ProfileActions -->|Set Password| ClickSetPassword[Click 'Set Password']
    ProfileActions -->|View Only| End([End])
    
    ClickEdit --> EditForm[Load Edit Profile Form]
    EditForm --> DisplayFields[Display Editable Fields:<br/>- Profile Picture<br/>- College<br/>- Course<br/>- Year<br/>- Block<br/>- School ID]
    
    DisplayFields --> FillForm[Fill/Update Form Fields]
    FillForm --> UploadPicture{Upload New Picture?}
    
    UploadPicture -->|Yes| SelectPicture[Select Profile Picture]
    UploadPicture -->|No| ValidateForm
    SelectPicture --> ValidatePicture{Valid Image?}
    
    ValidatePicture -->|No| ShowImageError[Show Image Error]
    ShowImageError --> SelectPicture
    ValidatePicture -->|Yes| ValidateForm
    
    ValidateForm[Validate Form Data] --> FormValid{Form Valid?}
    FormValid -->|No| ShowErrors[Show Validation Errors]
    ShowErrors --> FillForm
    
    FormValid -->|Yes| SaveProfile[Save Profile Updates]
    SaveProfile --> UpdateDatabase[Update Profile in Database]
    UpdateDatabase --> HandlePicture{Has Picture?}
    
    HandlePicture -->|Yes| SavePicture[Save Profile Picture to Media]
    HandlePicture -->|No| UpdateComplete
    SavePicture --> UpdateComplete[Profile Updated]
    UpdateComplete --> ShowSuccess[Show 'Successfully Updated' Message]
    ShowSuccess --> ViewProfile
    
    ClickPassword --> CheckPassword{Has Password?}
    CheckPassword -->|No| ClickSetPassword
    CheckPassword -->|Yes| PasswordForm[Load Password Change Form]
    
    PasswordForm --> EnterCurrent[Enter Current Password]
    EnterCurrent --> EnterNew[Enter New Password]
    EnterNew --> ConfirmNew[Confirm New Password]
    ConfirmNew --> ValidatePassword[Validate Password]
    
    ValidatePassword --> PasswordValid{Valid?}
    PasswordValid -->|No| ShowPasswordError[Show Password Error]
    ShowPasswordError --> EnterCurrent
    
    PasswordValid -->|Yes| CheckMatch{Passwords Match?}
    CheckMatch -->|No| ShowMatchError[Show 'Passwords Do Not Match' Error]
    ShowMatchError --> EnterNew
    
    CheckMatch -->|Yes| VerifyCurrent{Current Password Correct?}
    VerifyCurrent -->|No| ShowCurrentError[Show 'Incorrect Current Password' Error]
    ShowCurrentError --> EnterCurrent
    
    VerifyCurrent -->|Yes| UpdatePassword[Update User Password]
    UpdatePassword --> HashPassword[Hash New Password]
    HashPassword --> SavePassword[Save to Database]
    SavePassword --> PasswordSuccess[Show 'Password Changed Successfully' Message]
    PasswordSuccess --> ViewProfile
    
    ClickSetPassword --> SetPasswordForm[Load Set Password Form]
    SetPasswordForm --> EnterNewSet[Enter New Password]
    EnterNewSet --> ConfirmNewSet[Confirm New Password]
    ConfirmNewSet --> ValidateSetPassword[Validate Password]
    
    ValidateSetPassword --> SetPasswordValid{Valid?}
    SetPasswordValid -->|No| ShowSetPasswordError[Show Password Error]
    ShowSetPasswordError --> EnterNewSet
    
    SetPasswordValid -->|Yes| CheckSetMatch{Passwords Match?}
    CheckSetMatch -->|No| ShowSetMatchError[Show 'Passwords Do Not Match' Error]
    ShowSetMatchError --> EnterNewSet
    
    CheckSetMatch -->|Yes| SetPassword[Set User Password]
    SetPassword --> HashSetPassword[Hash Password]
    HashSetPassword --> SaveSetPassword[Save to Database]
    SaveSetPassword --> SetPasswordSuccess[Show 'Password Set Successfully' Message]
    SetPasswordSuccess --> ViewProfile
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style ShowErrors fill:#ffcdd2
    style ShowPasswordError fill:#ffcdd2
    style ShowMatchError fill:#ffcdd2
    style ShowCurrentError fill:#ffcdd2
    style UpdateComplete fill:#c8e6c9
    style PasswordSuccess fill:#c8e6c9
    style SetPasswordSuccess fill:#c8e6c9
```

## Process Steps:

1. **View Profile**
   - User accesses profile page
   - System displays current profile information
   - Shows profile picture, college, course details

2. **Edit Profile**
   - User clicks 'Update Profile'
   - System loads edit form
   - User can update:
     - Profile picture
     - College
     - Course
     - Year
     - Block
     - School ID
   - Validates and saves changes

3. **Change Password**
   - User clicks 'Change Password'
   - System checks if password exists
   - User enters:
     - Current password
     - New password
     - Confirm new password
   - Validates all inputs
   - Updates password in database

4. **Set Password**
   - For users without password (OAuth users)
   - User enters new password twice
   - Validates password strength
   - Sets password in database

5. **Validation**
   - All forms validate input
   - Password must meet requirements
   - Profile picture must be valid image
   - Shows appropriate error messages

