import customtkinter as ctk  # Importing the custom tkinter library as ctk
from tkinter import messagebox  # Importing the messagebox module from tkinter for displaying messages
import mysql.connector  # Importing the MySQL Connector Python module
from mysql.connector import Error  # Importing the Error class from mysql.connector
import os
import base64
import hashlib
import re
import random
import smtplib
from email.mime.text import MIMEText

# ==========================
#   DB CONFIG
# ==========================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "calladoctor1234",
    "database": "calladoctor",
}

# ==========================
#   EMAIL CONFIG
# ==========================
# Using Gmail with App Password.
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_ADDRESS = "linkeshjpr.25@gmail.com"
# App password MUST be without spaces:
EMAIL_PASSWORD = "gdnmwsbcljegppkp"


# ==========================
#   PASSWORD HASHING + POLICY
# ==========================

PBKDF2_ITERATIONS = 100_000
SALT_SIZE = 16  # bytes

# ==========================
#   OTP STATE (MODULE-LEVEL)
# ==========================
generated_otp = None
otp_verified = False
current_username = None


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using PBKDF2-HMAC-SHA256 with a random salt.
    Returns a base64 string containing salt+derived_key.
    This is compatible with verify_password() used in main_page.py.
    """
    if plain_password is None:
        raise ValueError("Password cannot be None")

    salt = os.urandom(SALT_SIZE)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return base64.b64encode(salt + dk).decode("utf-8")


def check_password_policy(password: str):
    """
    Basic password strength policy:
    - At least 8 characters
    - At least one lowercase, one uppercase, one digit, and one special character
    Returns (ok: bool, message: str | None)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."

    if not any(c in "!@#$%^&*()-_=+[]{};:,.<>/?\\" for c in password):
        return False, "Password must contain at least one special character."

    return True, None


# Function to go back to the main login page
def back_to_login(window):
    window.destroy()  # Destroying the current window
    import main_page  # Importing the main_page module
    main_page.create_login_window()  # Calling the create_login_window function from main_page


def _get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def _send_otp_email(to_email: str, otp: int):
    """
    Sends the OTP to the user's email using SMTP.
    """
    body = (
        f"Dear user,\n\n"
        f"Your Call a Doctor password reset OTP is: {otp}\n\n"
        f"If you did not request this, you can ignore this email.\n\n"
        f"Regards,\nCall a Doctor"
    )

    msg = MIMEText(body)
    msg["Subject"] = "Call a Doctor - Password Reset OTP"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)


def send_otp():
    """
    Step 1: Validate username exists, generate OTP, send it via EMAIL,
    and lock this username for the reset flow.
    """
    global generated_otp, otp_verified, current_username

    username = username_entry.get().strip()
    if not username:
        messagebox.showerror("Error", "Please enter your username first.")
        return

    connection = None
    try:
        connection = _get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, email FROM users WHERE username=%s", (username,))
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("Error", "Username not found.")
            return

        user_id, email = result
        if not email:
            messagebox.showerror("Error", "No email is registered for this user.")
            return

        generated_otp = random.randint(100000, 999999)
        otp_verified = False
        current_username = username

        # Send via email
        try:
            _send_otp_email(email, generated_otp)
        except Exception as e:
            print("Email error:", e)
            messagebox.showerror(
                "Error",
                "Failed to send OTP email. Please check email configuration.",
            )
            generated_otp = None
            current_username = None
            return

        messagebox.showinfo(
            "OTP Sent",
            "An OTP has been sent to your registered email address."
        )

        # Optionally disable username editing after OTP sent to avoid confusion
        username_entry.configure(state="disabled")

    except Error as e:
        print(f"The error '{e}' occurred")
        messagebox.showerror("Error", f"An error occurred while generating OTP: {e}")
    finally:
        try:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
        except Exception:
            pass


def verify_otp():
    """
    Step 2: Check the OTP entered by user.
    On success, enable password fields + Reset button.
    """
    global otp_verified

    if generated_otp is None or current_username is None:
        messagebox.showerror("Error", "Please request an OTP first.")
        return

    entered_otp = otp_entry.get().strip()
    if not entered_otp:
        messagebox.showerror("Error", "Please enter the OTP.")
        return

    if not entered_otp.isdigit():
        messagebox.showerror("Error", "OTP must contain only digits.")
        return

    if int(entered_otp) != generated_otp:
        messagebox.showerror("Error", "Invalid OTP. Please try again.")
        return

    # OTP correct
    otp_verified = True
    messagebox.showinfo("Success", "OTP verified successfully. You can now reset your password.")

    # Enable password fields and reset button
    new_password_entry.configure(state="normal")
    confirm_password_entry.configure(state="normal")
    reset_password_button.configure(state="normal")


# Function to reset the password (Step 3)
def reset_password():
    global otp_verified, current_username

    # Enforce OTP verification
    if not otp_verified or current_username is None:
        messagebox.showerror("Error", "Please verify the OTP before resetting your password.")
        return

    username_in_box = username_entry.get().strip()
    if username_in_box and username_in_box != current_username:
        messagebox.showerror("Error", "Username has changed. Please restart the reset process.")
        return

    username = current_username
    new_password = new_password_entry.get()
    confirm_password = confirm_password_entry.get()

    # Checking if any of the fields are empty
    if not new_password or not confirm_password:
        messagebox.showerror("Error", "Please fill out all password fields.")
        return

    # Checking if the new password matches the confirm password
    if new_password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match")
        return

    # Password strength policy
    ok, msg = check_password_policy(new_password)
    if not ok:
        messagebox.showerror("Weak Password", msg)
        return

    connection = None
    try:
        # Establishing a connection to MySQL database
        connection = _get_connection()
        cursor = connection.cursor()

        # Check if username still exists (paranoid check)
        cursor.execute("SELECT user_id FROM users WHERE username=%s", (username,))
        result = cursor.fetchone()

        # If username exists in the database
        if result:
            user_id = result[0]

            # Hash the new password before saving
            hashed_password = hash_password(new_password)

            cursor.execute(
                "UPDATE users SET password=%s WHERE user_id=%s",
                (hashed_password, user_id)
            )

            # Optional: clear lockout attempts for this username
            try:
                cursor.execute(
                    "DELETE FROM login_attempts WHERE username=%s",
                    (username,)
                )
            except Exception:
                # If login_attempts table doesn't exist or fails, ignore silently
                pass

            connection.commit()
            messagebox.showinfo("Success", "Password reset successfully")

            # Reset OTP state
            otp_verified = False

            forgot_password_window.destroy()
            import main_page
            main_page.create_login_window()
        else:
            messagebox.showerror("Error", "Username not found")
    except Error as e:
        print(f"The error '{e}' occurred")
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        try:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
        except Exception:
            pass


# Create forgot password window
def create_forgot_password_window():
    global forgot_password_window
    global username_entry, new_password_entry, confirm_password_entry, otp_entry, reset_password_button

    ctk.set_appearance_mode("light")  # Setting appearance mode to light
    ctk.set_default_color_theme("blue")  # Setting default color theme to blue

    forgot_password_window = ctk.CTk()  # Creating a custom tkinter window
    forgot_password_window.title("Forgot Password")  # Setting window title
    forgot_password_window.geometry("400x500")  # Slightly taller for OTP field

    # Username
    username_label = ctk.CTkLabel(forgot_password_window, text="Username")
    username_label.pack(pady=10)
    username_entry = ctk.CTkEntry(forgot_password_window)
    username_entry.pack(pady=5)

    # OTP section
    otp_label = ctk.CTkLabel(forgot_password_window, text="OTP")
    otp_label.pack(pady=10)
    otp_entry = ctk.CTkEntry(forgot_password_window)
    otp_entry.pack(pady=5)

    send_otp_button = ctk.CTkButton(
        forgot_password_window,
        text="Send OTP",
        command=send_otp
    )
    send_otp_button.pack(pady=5)

    verify_otp_button = ctk.CTkButton(
        forgot_password_window,
        text="Verify OTP",
        command=verify_otp
    )
    verify_otp_button.pack(pady=5)

    # New password (initially disabled until OTP verified)
    new_password_label = ctk.CTkLabel(forgot_password_window, text="New Password")
    new_password_label.pack(pady=10)
    new_password_entry = ctk.CTkEntry(forgot_password_window, show='*', state="disabled")
    new_password_entry.pack(pady=5)

    confirm_password_label = ctk.CTkLabel(forgot_password_window, text="Confirm Password")
    confirm_password_label.pack(pady=10)
    confirm_password_entry = ctk.CTkEntry(forgot_password_window, show='*', state="disabled")
    confirm_password_entry.pack(pady=5)

    # Reset Password button (disabled until OTP verified)
    reset_password_button = ctk.CTkButton(
        forgot_password_window,
        text="Reset Password",
        command=reset_password,
        state="disabled"
    )
    reset_password_button.pack(pady=20)

    # Back button
    back_button = ctk.CTkButton(
        forgot_password_window,
        text="Back",
        command=lambda: back_to_login(forgot_password_window)
    )
    back_button.pack(pady=10)

    forgot_password_window.mainloop()  # Running main loop for the window


if __name__ == "__main__":
    create_forgot_password_window()  # Calling the create_forgot_password_window function if the script is executed directly
