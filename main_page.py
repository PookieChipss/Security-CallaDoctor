import customtkinter as ctk  # Import customtkinter for creating custom UI elements
from tkinter import messagebox  # Import messagebox for showing dialog boxes
from PIL import Image, ImageDraw  # Import PIL for image processing
import mysql.connector  # Import mysql.connector for database connectivity
from mysql.connector import Error  # Import Error for handling database errors
import subprocess  # Import subprocess for running external scripts
import os
import base64
import hashlib
import hmac
from datetime import datetime, timedelta

# ==========================
#   DATABASE CONFIG
# ==========================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "calladoctor1234",
    "database": "calladoctor",
}

# ==========================
#   PASSWORD HASHING
#   PBKDF2 + random salt
# ==========================

PBKDF2_ITERATIONS = 100_000
SALT_SIZE = 16  # bytes


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using PBKDF2-HMAC-SHA256 with a random salt.
    Returns a base64 string containing salt+derived_key.
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


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verify a plaintext password against a stored base64(salt+dk) hash.
    Returns False if anything is invalid.
    """
    try:
        raw = base64.b64decode(stored_hash.encode("utf-8"))
        salt = raw[:SALT_SIZE]
        dk_stored = raw[SALT_SIZE:]
        dk_new = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            PBKDF2_ITERATIONS,
        )
        return hmac.compare_digest(dk_stored, dk_new)
    except Exception:
        # Not a valid hash or corrupted value
        return False


# ==========================
#   LOGIN LOCKOUT
# ==========================
# We auto-create this table if it doesn't exist:
#
#   CREATE TABLE login_attempts (
#       username       VARCHAR(255) PRIMARY KEY,
#       failed_attempts INT NOT NULL DEFAULT 0,
#       locked_until   DATETIME NULL
#   );
#

LOCK_THRESHOLD = 5          # number of failed attempts before lock
LOCK_MINUTES = 10           # lock duration in minutes


def _get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def _ensure_login_attempts_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS login_attempts (
            username       VARCHAR(255) PRIMARY KEY,
            failed_attempts INT NOT NULL DEFAULT 0,
            locked_until   DATETIME NULL
        )
        """
    )


def is_account_locked(username: str):
    """
    Returns (locked: bool, locked_until: datetime | None).
    Automatically clears expired locks.
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        _ensure_login_attempts_table(cursor)

        cursor.execute(
            "SELECT failed_attempts, locked_until FROM login_attempts WHERE username=%s",
            (username,),
        )
        row = cursor.fetchone()
        if not row:
            return False, None

        failed_attempts, locked_until = row
        now = datetime.now()

        if locked_until and locked_until > now:
            # still locked
            return True, locked_until

        # lock expired -> reset record
        if locked_until and locked_until <= now:
            cursor.execute(
                "UPDATE login_attempts "
                "SET failed_attempts = 0, locked_until = NULL "
                "WHERE username=%s",
                (username,),
            )
            conn.commit()

        return False, None
    except Error:
        # Fail open if DB error (no artificial lock)
        return False, None
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


def register_failed_login(username: str):
    """
    Increment failed login attempts; lock account if threshold exceeded.
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        _ensure_login_attempts_table(cursor)

        cursor.execute(
            "SELECT failed_attempts FROM login_attempts WHERE username=%s",
            (username,),
        )
        row = cursor.fetchone()
        now = datetime.now()

        if not row:
            # first failure for this username
            cursor.execute(
                "INSERT INTO login_attempts (username, failed_attempts, locked_until) "
                "VALUES (%s, %s, NULL)",
                (username, 1),
            )
        else:
            failed_attempts = row[0] + 1
            if failed_attempts >= LOCK_THRESHOLD:
                lock_until = now + timedelta(minutes=LOCK_MINUTES)
                cursor.execute(
                    "UPDATE login_attempts "
                    "SET failed_attempts=%s, locked_until=%s "
                    "WHERE username=%s",
                    (failed_attempts, lock_until, username),
                )
            else:
                cursor.execute(
                    "UPDATE login_attempts "
                    "SET failed_attempts=%s "
                    "WHERE username=%s",
                    (failed_attempts, username),
                )

        conn.commit()
    except Error:
        # Don't crash on logging failure
        pass
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


def reset_failed_logins(username: str):
    """
    Clear failed login attempts after a successful login.
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        _ensure_login_attempts_table(cursor)
        cursor.execute("DELETE FROM login_attempts WHERE username=%s", (username,))
        conn.commit()
    except Error:
        pass
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


# ==========================
#   UI HELPERS
# ==========================

# Function to create a rounded image
def create_rounded_image(image_path, size, corner_radius):
    # Open and resize the image
    image = Image.open(image_path).resize(size, Image.Resampling.LANCZOS).convert("RGBA")
    # Create a mask for rounded corners
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), corner_radius, fill=255)
    # Create a new image with rounded corners
    rounded_image = Image.new("RGBA", image.size)
    rounded_image.paste(image, (0, 0), mask)
    return rounded_image


# Function to open the register page
def open_register_page():
    login_root.destroy()  # Close the login window
    import register_page  # Import the register page script
    register_page.create_register_window()  # Open the register window


# Event handler for entry click
def on_entry_click(event, entry, default_text):
    if entry.get() == default_text:  # Check if the entry contains default text
        entry.delete(0, "end")  # Clear the entry
        entry.insert(0, '')  # Insert an empty string
        entry.configure(text_color='black')  # Change text color to black
        if entry == password_entry:
            entry.configure(show='*')  # Mask the password entry


# Event handler for focus out
def on_focusout(event, entry, default_text):
    if entry.get() == '':  # Check if the entry is empty
        entry.insert(0, default_text)  # Insert the default text
        entry.configure(text_color='grey')  # Change text color to grey
        if entry == password_entry:
            entry.configure(show='')  # Unmask the password entry


# ==========================
#   AUTHENTICATION LOGIC
# ==========================

# Function to authenticate the user
def authenticate_user(username, password):
    username = username.strip()

    # ---- 1) Check account lock before querying password ----
    locked, locked_until = is_account_locked(username)
    if locked:
        msg = "Your account is temporarily locked due to multiple failed login attempts."
        if locked_until:
            msg += f"\nTry again after {locked_until.strftime('%Y-%m-%d %H:%M:%S')}."
        messagebox.showerror("Login Failed", msg)
        return None

    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            passwd=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        cursor = connection.cursor()

        # Fetch stored password hash/plaintext and user meta
        cursor.execute(
            "SELECT user_id, role, fullname, password FROM users WHERE username=%s",
            (username,),
        )
        row = cursor.fetchone()

        if not row:
            # Unknown username -> still count as failure
            connection.close()
            register_failed_login(username)
            return None

        user_id, role, fullname, stored_password = row

        if stored_password is None:
            connection.close()
            register_failed_login(username)
            return None

        # ---- 2) Verify hashed password (preferred path) ----
        valid = False
        used_hash_mode = False

        if verify_password(password, stored_password):
            valid = True
            used_hash_mode = True
        else:
            # ---- 3) BACKWARDS COMPATIBILITY:
            # If stored_password is actually plaintext (old system),
            # allow it ONCE and then upgrade to hashed.
            if stored_password == password:
                valid = True
                used_hash_mode = False

        if not valid:
            connection.close()
            register_failed_login(username)
            return None

        # Successful login: reset failed attempts
        reset_failed_logins(username)

        # If password was stored in plaintext, upgrade to hash now
        if not used_hash_mode:
            try:
                new_hash = hash_password(password)
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE users SET password=%s WHERE user_id=%s",
                    (new_hash, user_id),
                )
                connection.commit()
            except Error:
                # Don't break login if upgrade fails
                pass

        # ---- 4) Existing role-specific logic ----
        if role == 'doctor':
            # Check if the user is a doctor
            cursor.execute("SELECT doctor_id FROM doctors WHERE user_id=%s", (user_id,))
            doctor_result = cursor.fetchone()
            doctor_id = doctor_result[0] if doctor_result else None
            connection.close()
            return role, doctor_id, fullname

        elif role == 'clinic_admin':
            # Check if the user is a clinic admin
            cursor.execute(
                "SELECT c.clinic_id, c.is_approved "
                "FROM admin_clinics ac "
                "JOIN clinics c ON ac.clinic_id = c.clinic_id "
                "WHERE ac.admin_id=%s",
                (user_id,),
            )
            clinic_result = cursor.fetchone()
            clinic_id, is_approved = clinic_result if clinic_result else (None, None)
            if is_approved == 0:
                connection.close()
                messagebox.showerror(
                    "Login Failed",
                    "Clinic registration is pending approval. Please try again later.",
                )
                return None
            connection.close()
            return role, clinic_id, fullname

        elif role == 'patient':
            # Check if the user is a patient
            cursor.execute("SELECT patient_id FROM patients WHERE user_id=%s", (user_id,))
            patient_result = cursor.fetchone()
            patient_id = patient_result[0] if patient_result else None
            connection.close()
            return role, patient_id, fullname

        else:
            connection.close()
            return role, None, fullname

    except Error as e:
        print(f"The error '{e}' occurred")
        messagebox.showerror("Error", f"Database error: {e}")
        return None


# Function to handle login
def login():
    username = username_entry.get()
    password = password_entry.get()

    # Strip placeholder and whitespace
    if username == "Username":
        username = ""
    if password == "Password":
        password = ""

    username = username.strip()
    password = password.strip()

    if not username or not password:
        messagebox.showerror("Login Failed", "Please fill out all fields")
        return

    # Optional: basic length sanity check (defence-in-depth)
    if len(username) > 255 or len(password) > 255:
        messagebox.showerror("Login Failed", "Username or password is too long.")
        return

    result = authenticate_user(username, password)  # Authenticate the user
    print(f"Login result: {result}")  # Debug print statement

    if result:
        role, id, fullname = result
        if role == 'doctor' and id is None:
            messagebox.showerror("Login Failed", "Doctor ID not found")
            return

        login_root.destroy()  # Close the login window

        if role == 'admin':
            subprocess.run(['python', 'adminhome.py', fullname])
        elif role == 'clinic_admin':
            subprocess.run(['python', 'adminclinichome.py', str(id), fullname])
        elif role == 'doctor':
            subprocess.run(['python', 'doctorhome.py', str(id)])
        elif role == 'patient':
            subprocess.run(['python', 'patienthome.py', str(id), fullname])
    else:
        # Error messages for lockout / DB errors are shown inside authenticate_user.
        # Here we keep a generic message for wrong credentials.
        messagebox.showerror("Login Failed", "Invalid username or password")


# Function to open the forgot password page
def open_forgot_password_page():
    login_root.destroy()  # Close the login window
    subprocess.run(['python', 'forgot_password.py'])  # Run the forgot password script


# Function to create the login window
def create_login_window():
    global login_root, password_entry, username_entry
    ctk.set_appearance_mode("light")  # Set the appearance mode
    ctk.set_default_color_theme("blue")  # Set the default color theme

    login_root = ctk.CTk()  # Create the main window
    login_root.title("Login")  # Set the window title
    width = 880
    height = 650
    login_root.geometry(f"{width}x{height}")  # Set the window size

    top_frame = ctk.CTkFrame(login_root, fg_color="#ADD8E6", width=width, height=height)
    top_frame.pack(fill="both", expand=True)  # Create and pack the top frame

    logo_path = "C://Users//user//Documents//GitHub//SoftwareEng//Software_Project//Harvind//Images//SoftwareLogo.png"
    logo_image = create_rounded_image(logo_path, (150, 150), 30)  # Create a rounded logo image
    logo_photo = ctk.CTkImage(light_image=logo_image, size=(150, 150))
    logo_label = ctk.CTkLabel(top_frame, image=logo_photo, fg_color="#ADD8E6", text="")
    logo_label.place(x=width-10, y=10, anchor="ne")  # Place the logo image

    welcome_label = ctk.CTkLabel(
        top_frame,
        text="Welcome to Login",
        font=("Arial", 24, "bold"),
        fg_color="#ADD8E6",
        text_color="#000080"
    )
    welcome_label.place(relx=0.5, rely=0.2, anchor="center")  # Place the welcome label

    user_icon_path = "C://Users//user//Documents//GitHub//SoftwareEng//Software_Project//Harvind//Images//Patientnobg.png"
    user_icon = create_rounded_image(user_icon_path, (150, 150), 20)  # Create a rounded user icon
    user_photo = ctk.CTkImage(light_image=user_icon, size=(150, 150))
    user_icon_label = ctk.CTkLabel(top_frame, image=user_photo, fg_color="#ADD8E6", text="")
    user_icon_label.place(relx=0.5, rely=0.35, anchor="center")  # Place the user icon

    default_username = "Username"
    default_password = "Password"

    username_entry = ctk.CTkEntry(
        top_frame,
        font=("Arial", 16),
        fg_color="white",
        text_color='grey',
        width=300,
        height=30
    )
    username_entry.insert(0, default_username)
    username_entry.bind('<FocusIn>', lambda event: on_entry_click(event, username_entry, default_username))
    username_entry.bind('<FocusOut>', lambda event: on_focusout(event, username_entry, default_username))
    username_entry.place(relx=0.5, rely=0.5, anchor="center")  # Create and place the username entry

    password_entry = ctk.CTkEntry(
        top_frame,
        font=("Arial", 16),
        fg_color="white",
        text_color='grey',
        show='*',
        width=300,
        height=30
    )
    password_entry.insert(0, default_password)
    password_entry.bind('<FocusIn>', lambda event: on_entry_click(event, password_entry, default_password))
    password_entry.bind('<FocusOut>', lambda event: on_focusout(event, password_entry, default_password))
    password_entry.place(relx=0.5, rely=0.55, anchor="center")  # Create and place the password entry

    login_button = ctk.CTkButton(
        top_frame,
        text="Login",
        font=("Arial", 16),
        command=login,
        fg_color="#4682B4",
        hover_color="#5A9BD4",
        text_color="white"
    )
    login_button.place(relx=0.5, rely=0.6, anchor="center")  # Create and place the login button

    forgot_password_label = ctk.CTkLabel(
        top_frame,
        text="Forgot Password?",
        font=("Arial", 12),
        fg_color="#ADD8E6",
        text_color="#0000EE",
        cursor="hand2"
    )
    forgot_password_label.place(relx=0.5, rely=0.65, anchor="center")
    forgot_password_label.bind("<Button-1>", lambda event: open_forgot_password_page())  # Create and place the forgot password label

    login_frame = ctk.CTkFrame(top_frame, fg_color="#ADD8E6")
    login_frame.place(relx=0.99, rely=0.99, anchor="se")  # Create and place the login frame

    login_label_text = ctk.CTkLabel(
        login_frame,
        text="Don't have an account? ",
        font=("Arial", 16),
        fg_color="#ADD8E6",
        text_color="black"
    )
    login_label_text.pack(side="left")  # Create and place the login label text

    click_here_register_label = ctk.CTkLabel(
        login_frame,
        text="Click here",
        font=("Arial", 16),
        fg_color="#ADD8E6",
        text_color="#0000EE",
        cursor="hand2"
    )
    click_here_register_label.pack(side="left")
    click_here_register_label.bind("<Button-1>", lambda event: open_register_page())  # Create and place the register label

    login_root.mainloop()  # Start the main loop


if __name__ == "__main__":
    create_login_window()  # Call function to create the login window
