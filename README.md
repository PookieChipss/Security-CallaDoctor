# Call a Doctor – Security-Enhanced Version

This repository contains a modified version of the **Call a Doctor** desktop app (Python + CustomTkinter + MySQL) for a security coursework.  
The focus is on **hardening authentication and password reset flows** while keeping the original system behaviour.

---

## 🔐 Security Features Implemented

1. **Secure Password Hashing (PBKDF2 + Salt)**
   - All new passwords are stored as **PBKDF2-HMAC-SHA256** hashes with a random 16-byte salt.
   - Implemented in:
     - `patientregister.py`
     - `clinicregister.py`
     - `adddoctor.py`
     - `forgot_password.py`
   - `main_page.py` verifies passwords using the same algorithm.
   - If an old account still has a plaintext password, it is **auto-migrated to a hash on first successful login**.

2. **Password Strength Policy**
   - Enforced during registration and password reset.
   - Requirements:
     - Minimum 8 characters
     - At least one **uppercase**, **lowercase**, **digit**, and **special character**
   - Implemented via `check_password_policy(...)` in:
     - `patientregister.py`
     - `clinicregister.py`
     - `adddoctor.py`
     - `forgot_password.py`

3. **Account Lockout / Brute-Force Protection**
   - After **5 failed login attempts** for the same username, the account is locked for **10 minutes**.
   - Implemented in `main_page.py` with helper functions:
     - `is_account_locked(...)`
     - `register_failed_login(...)`
     - `reset_failed_logins(...)`
   - Uses a dedicated table in MySQL:

     ```sql
     CREATE TABLE login_attempts (
         username        VARCHAR(255) PRIMARY KEY,
         failed_attempts INT NOT NULL DEFAULT 0,
         locked_until    DATETIME NULL
     );
     ```

4. **Email-Based OTP Password Reset**
   - “Forgot Password” flow now requires a **one-time password (OTP)** sent to the user’s registered email.
   - Flow:
     1. User enters username → system validates it.
     2. A 6-digit OTP is generated and **emailed** via SMTP.
     3. User must enter the correct OTP → only then can they set a new password.
     4. New password must pass the strength policy and is stored as a PBKDF2 hash.
     5. Any existing lockout state for that username is cleared.
   - Implemented in `forgot_password.py`:
     - `_send_otp_email(...)`
     - `send_otp()`, `verify_otp()`, `reset_password()`

---

## 🛠 Tech Stack

- **Language:** Python 3.x  
- **GUI:** CustomTkinter, Tkinter  
- **Database:** MySQL  
- **Email:** SMTP (Gmail with App Password)  
- **Other libs:** `mysql-connector-python`, `Pillow`, `tkcalendar`, `smtplib`

---

## ⚙️ Setup

1. **Clone the project and install dependencies**

   ```bash
   pip install customtkinter mysql-connector-python pillow tkcalendar
