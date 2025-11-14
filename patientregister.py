import customtkinter as ctk  # Import customtkinter module (assuming it's a custom tkinter library)
from tkinter import messagebox  # Import messagebox from tkinter for displaying messages
from tkcalendar import DateEntry  # Import DateEntry widget from tkcalendar
import re  # Import re module for regular expressions
import mysql.connector  # Import mysql.connector for MySQL database connection
from mysql.connector import Error  # Import Error class from mysql.connector
import os
import base64
import hashlib

# ==========================
#   PASSWORD HASHING + POLICY
# ==========================

PBKDF2_ITERATIONS = 100_000
SALT_SIZE = 16  # bytes


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using PBKDF2-HMAC-SHA256 with a random salt.
    Returns a base64 string containing salt+derived_key.
    This format is compatible with verify_password() in main_page.py.
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
    Basic password strength policy used at registration:
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


def create_form(frame):
    labels = ["Fullname:", "Username:", "Password:", "Confirm Password:", "Gender:", "Address:", "IC:", "Date of Birth:", "Email:", "Tel:"]
    entries = {}

    # Loop to create labels and entries
    for i, label_text in enumerate(labels):
        row = i // 2
        col = i % 2 * 2
        label = ctk.CTkLabel(frame, text=label_text, font=("Helvetica", 14), text_color="black")
        label.grid(row=row, column=col, sticky="e", pady=5, padx=5)  # Grid layout for labels

        if label_text == "Date of Birth:":
            entry = DateEntry(frame, font=("Helvetica", 14), date_pattern='y-mm-dd')
        elif label_text == "Gender:":
            entry = ctk.CTkComboBox(frame, values=["Male", "Female"], font=("Helvetica", 14),
                                    fg_color="white", text_color="black")
            entry.set("Male")  # Set default value for ComboBox
        else:
            entry = ctk.CTkEntry(
                frame,
                font=("Helvetica", 14),
                fg_color="white",
                text_color="black",
                show="*" if "Password" in label_text else ""
            )
            if label_text == "Tel:":
                entry.configure(
                    validate="key",
                    validatecommand=(frame.register(validate_tel), '%P')
                )  # Validate Tel entry
            if label_text == "IC:":
                entry.configure(
                    validate="key",
                    validatecommand=(frame.register(validate_ic), '%P')
                )  # Validate IC entry

        entry.grid(row=row, column=col + 1, pady=5, padx=5, sticky="ew")  # Grid layout for entries
        entries[label_text] = entry  # Store entry widget in entries dictionary

    # Configure grid row and column weights
    for i in range(len(labels) // 2 + 1):
        frame.grid_rowconfigure(i, weight=1)
    for j in range(4):
        frame.grid_columnconfigure(j, weight=1)

    return entries


def validate_tel(value_if_allowed):
    """ Validate that the input for the Tel field matches the Malaysian phone number format. """
    pattern = re.compile(r'^\d{0,3}-?\d{0,8}$')  # Define regex pattern for Malaysian phone number
    if pattern.match(value_if_allowed):
        return True
    else:
        return False


def validate_ic(value_if_allowed):
    """ Validate that the input for the IC field matches the Malaysian IC format. """
    pattern = re.compile(r'^\d{0,6}-?\d{0,2}-?\d{0,4}$')  # Define regex pattern for Malaysian IC number
    if pattern.match(value_if_allowed):
        return True
    else:
        return False


def back(root):
    root.destroy()  # Destroy current window
    import main_page  # Import main_page module
    main_page.create_login_window()  # Call create_login_window function from main_page module


def register(entries, root):
    data = {label: entry.get() for label, entry in entries.items()}  # Get data from entry widgets
    missing_data = [label for label, entry in data.items() if not entry]  # Find missing entries

    if missing_data:
        messagebox.showerror("Error", f"Please fill all the fields: {', '.join(missing_data)}")
        return

    if data["Password:"] != data["Confirm Password:"]:
        messagebox.showerror("Error", "Passwords do not match!")
        return

    # Password strength check (security feature)
    ok, msg = check_password_policy(data["Password:"])
    if not ok:
        messagebox.showerror("Weak Password", msg)
        return

    # Optional: simple email format check (defence-in-depth)
    email_pattern = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
    if not email_pattern.match(data["Email:"]):
        messagebox.showerror("Error", "Please enter a valid email address.")
        return

    # Save user data to the database
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='calladoctor1234',
            database='calladoctor'
        )
        cursor = connection.cursor()

        # Check for duplicate entries
        cursor.execute("SELECT 1 FROM users WHERE username = %s", (data["Username:"],))
        if cursor.fetchone() is not None:
            messagebox.showerror("Error", "Username already exists!")
            return

        cursor.execute("SELECT 1 FROM users WHERE email = %s", (data["Email:"],))
        if cursor.fetchone() is not None:
            messagebox.showerror("Error", "Email already exists!")
            return

        cursor.execute("SELECT 1 FROM users WHERE phone_number = %s", (data["Tel:"],))
        if cursor.fetchone() is not None:
            messagebox.showerror("Error", "Phone number already exists!")
            return

        cursor.execute(
            "SELECT 1 FROM patients WHERE identification_number = %s",
            (data["IC:"],)
        )
        if cursor.fetchone() is not None:
            messagebox.showerror("Error", "IC number already exists!")
            return

        # ---- HASH PASSWORD BEFORE INSERTING (security feature) ----
        hashed_pw = hash_password(data["Password:"])

        cursor.execute(
            '''
            INSERT INTO users (username, password, email, phone_number,
                               date_of_birth, address, fullname, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (
                data["Username:"],
                hashed_pw,
                data["Email:"],
                data["Tel:"],
                data["Date of Birth:"],
                data["Address:"],
                data["Fullname:"],
                'patient',
            )
        )
        user_id = cursor.lastrowid

        cursor.execute(
            '''
            INSERT INTO patients (user_id, fullname, identification_number, gender)
            VALUES (%s, %s, %s, %s)
            ''',
            (user_id, data["Fullname:"], data["IC:"], data["Gender:"])
        )
        connection.commit()  # Commit changes to the database

        messagebox.showinfo("Success", "Registration successful!")  # Show success message
        root.destroy()  # Destroy current window
        import main_page  # Import main_page module
        main_page.create_login_window()  # Call create_login_window function from main_page module

    except Error as e:
        messagebox.showerror("Error", f"Error occurred: {e}")  # Show error message
    finally:
        try:
            if connection.is_connected():
                cursor.close()
                connection.close()  # Close database connection
        except Exception:
            pass


def on_enter_back(event, back_button):
    back_button.configure(fg_color='#FF4500')  # Change button color on hover


def on_leave_back(event, back_button):
    back_button.configure(fg_color='#FF6347')  # Change button color back on leave


def on_enter_register(event, register_button):
    register_button.configure(fg_color='#228B22')  # Change button color on hover


def on_leave_register(event, register_button):
    register_button.configure(fg_color='#32CD32')  # Change button color back on leave


def create_patient_register_window():
    root = ctk.CTk()  # Create CTk root window
    root.configure(bg='lightblue')  # Set background color for the CTk window
    root.title("Call a Doctor")  # Set the title of the main window
    root.geometry("800x600")  # Set initial size of the main window

    ctk.set_appearance_mode("light")  # Set the appearance mode of customtkinter
    ctk.set_default_color_theme("blue")  # Set the default color theme of customtkinter

    title_label = ctk.CTkLabel(root, text="Call a Doctor", font=("Helvetica", 24, "bold"), text_color="black")
    title_label.pack(pady=10)  # Pack the title label with padding on y-axis

    subtitle_label = ctk.CTkLabel(root, text="Welcome to Registration", font=("Helvetica", 18), text_color="black")
    subtitle_label.pack(pady=10)  # Pack the subtitle label with padding on y-axis

    frame = ctk.CTkFrame(root, fg_color='#D3D3D3')
    frame.pack(pady=10, padx=20, expand=True, fill=ctk.BOTH)  # Pack the main frame with padding and expand to fill

    entries = create_form(frame)  # Call function to create the registration form

    # Back button configuration
    back_button = ctk.CTkButton(
        root,
        text="Back",
        fg_color='#FF6347',
        font=("Helvetica", 12),
        text_color="black",
        command=lambda: back(root)
    )
    back_button.pack(side=ctk.LEFT, padx=20, pady=10)  # Pack the back button to the left with padding

    # Register button configuration
    register_button = ctk.CTkButton(
        root,
        text="Register",
        fg_color='#32CD32',
        font=("Helvetica", 12),
        text_color="black",
        command=lambda: register(entries, root)
    )
    register_button.pack(side=ctk.RIGHT, padx=20, pady=10)  # Pack the register button to the right with padding

    # Bind events for hover effects on buttons
    back_button.bind("<Enter>", lambda event: on_enter_back(event, back_button))
    back_button.bind("<Leave>", lambda event: on_leave_back(event, back_button))
    register_button.bind("<Enter>", lambda event: on_enter_register(event, register_button))
    register_button.bind("<Leave>", lambda event: on_leave_register(event, register_button))

    root.mainloop()  # Run the main event loop


if __name__ == "__main__":
    create_patient_register_window()  # Call function to create patient registration window
