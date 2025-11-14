import customtkinter as ctk  # Import customtkinter for creating custom UI elements
from tkinter import messagebox, filedialog  # Import messagebox for showing dialog boxes and filedialog for file selection
from tkcalendar import DateEntry  # Import DateEntry from tkcalendar for date selection
import mysql.connector  # Import mysql.connector for database connectivity
from mysql.connector import Error  # Import Error for handling database errors
import os
import base64
import hashlib
import re

# ==========================
#   PASSWORD HASHING + POLICY
# ==========================

PBKDF2_ITERATIONS = 100_000
SALT_SIZE = 16  # bytes


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using PBKDF2-HMAC-SHA256 with a random salt.
    Returns a base64 string containing salt+derived_key.
    Compatible with login verification in main_page.py.
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
    Basic password strength policy used at clinic admin registration:
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


# Function to submit clinic data to the database
def submit_clinic_data(
    clinic_name,
    clinic_address,
    clinic_license_path,
    admin_fullname,
    admin_username,
    admin_password,
    admin_email,
    admin_phone_number,
    admin_date_of_birth,
    admin_address
):
    connection = None
    try:
        # Establish the database connection
        connection = mysql.connector.connect(
            host='localhost',  # Host where the database server is located
            user='root',  # Database username
            passwd='calladoctor1234',  # Database password
            database='calladoctor'  # Name of the database
        )
        cursor = connection.cursor()  # Create a cursor object to execute SQL queries

        # Check if the username already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (admin_username,))
        if cursor.fetchone() is not None:
            messagebox.showerror("Error", "Clinic username already exists!")  # Show error message if username exists
            return

        # Check if the email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (admin_email,))
        if cursor.fetchone() is not None:
            messagebox.showerror("Error", "Email already exists!")  # Show error message if email exists
            return

        # Check if the phone number already exists
        cursor.execute("SELECT * FROM users WHERE phone_number = %s", (admin_phone_number,))
        if cursor.fetchone() is not None:
            messagebox.showerror("Error", "Phone number already exists!")  # Show error message if phone number exists
            return

        # Insert clinic data
        with open(clinic_license_path, 'rb') as f:  # Open the clinic license file in binary mode
            clinic_license_data = f.read()  # Read the file content
        insert_clinic_query = """INSERT INTO clinics (clinic_name, address, clinic_license) VALUES (%s, %s, %s)"""
        clinic_data = (clinic_name, clinic_address, clinic_license_data)  # Data to be inserted into the clinics table
        cursor.execute(insert_clinic_query, clinic_data)  # Execute the query
        clinic_id = cursor.lastrowid  # Get the ID of the last inserted row (clinic ID)

        # ---- HASH ADMIN PASSWORD BEFORE INSERT (security feature) ----
        hashed_admin_password = hash_password(admin_password)

        # Insert user data
        insert_user_query = """
            INSERT INTO users (username, password, email, phone_number, date_of_birth, address, role, fullname)
            VALUES (%s, %s, %s, %s, %s, %s, 'clinic_admin', %s)
        """
        user_data = (
            admin_username,
            hashed_admin_password,
            admin_email,
            admin_phone_number,
            admin_date_of_birth,
            admin_address,
            admin_fullname
        )  # Data to be inserted into the users table
        cursor.execute(insert_user_query, user_data)  # Execute the query
        user_id = cursor.lastrowid  # Get the ID of the last inserted row (user ID)

        # Link admin to clinic
        insert_admin_clinic_query = """INSERT INTO admin_clinics (admin_id, clinic_id, user_id) VALUES (%s, %s, %s)"""
        admin_clinic_data = (user_id, clinic_id, user_id)  # Data to link the admin with the clinic
        cursor.execute(insert_admin_clinic_query, admin_clinic_data)  # Execute the query

        connection.commit()  # Commit the transaction to the database
        messagebox.showinfo(
            "Success",
            "Request for clinic registration has been sent! Wait for approval."
        )  # Show success message
        clinic_register_root.destroy()  # Close the registration window
        import main_page  # Import the main page module
        main_page.create_login_window()  # Open the login window
    except mysql.connector.Error as error:
        messagebox.showerror("Error", f"Failed to register clinic: {error}")  # Show error message if any database error occurs
    finally:
        if connection and connection.is_connected():
            cursor.close()  # Close the cursor
            connection.close()  # Close the database connection


# Function to browse and select a file
def browse_file():
    filename = filedialog.askopenfilename(
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
            ("All files", "*.*")
        ]
    )  # Open file dialog and allow selection of image files
    return filename  # Return the selected file path


# Function to create the clinic registration window
def create_clinic_register_window():
    global clinic_register_root, clinic_license_path
    clinic_license_path = None  # Initialize the variable to store the file path
    clinic_register_root = ctk.CTk()  # Create the main window for clinic registration
    clinic_register_root.title("Clinic Registration")  # Set the window title
    width = 600  # Set the window width
    height = 750  # Set the window height
    clinic_register_root.geometry(f"{width}x{height}")  # Set the window size

    ctk.set_appearance_mode("light")  # Set the appearance mode to light
    ctk.set_default_color_theme("blue")  # Set the default color theme to blue

    top_frame = ctk.CTkFrame(clinic_register_root)  # Create a frame to hold the top section of the window
    top_frame.pack(fill="both", expand=True)  # Pack the frame to fill the window

    title_label = ctk.CTkLabel(
        top_frame,
        text="Call a Doctor",
        font=("Helvetica", 24, "bold"),
        text_color="black"
    )  # Create a label for the title
    title_label.pack(pady=10)  # Pack the title label with padding

    sub_title_label = ctk.CTkLabel(
        top_frame,
        text="Welcome to Registration",
        font=("Helvetica", 18),
        text_color="black"
    )  # Create a label for the subtitle
    sub_title_label.pack(pady=10)  # Pack the subtitle label with padding

    form_frame = ctk.CTkFrame(top_frame)  # Create a frame to hold the form elements
    form_frame.pack(pady=10)  # Pack the form frame with padding

    # Clinic info section
    clinic_info_label = ctk.CTkLabel(
        form_frame,
        text="Clinic info",
        font=("Helvetica", 16),
        text_color="black"
    )  # Create a label for the clinic info section
    clinic_info_label.grid(row=0, column=0, columnspan=2, pady=1)  # Place the label in the grid

    clinic_name_label = ctk.CTkLabel(
        form_frame,
        text="Clinic Name:",
        font=("Helvetica", 14),
        text_color="black"
    )  # Create a label for the clinic name
    clinic_name_label.grid(row=1, column=0, sticky="e", pady=5)  # Place the label in the grid
    clinic_name_entry = ctk.CTkEntry(
        form_frame,
        font=("Helvetica", 14),
        fg_color="white",
        text_color="black"
    )  # Create an entry widget for the clinic name
    clinic_name_entry.grid(row=1, column=1, pady=5)  # Place the entry widget in the grid

    clinic_address_label = ctk.CTkLabel(
        form_frame,
        text="Clinic Address:",
        font=("Helvetica", 14),
        text_color="black"
    )  # Create a label for the clinic address
    clinic_address_label.grid(row=2, column=0, sticky="e", pady=5)  # Place the label in the grid
    clinic_address_entry = ctk.CTkEntry(
        form_frame,
        font=("Helvetica", 14),
        fg_color="white",
        text_color="black"
    )  # Create an entry widget for the clinic address
    clinic_address_entry.grid(row=2, column=1, pady=5)  # Place the entry widget in the grid

    clinic_license_label = ctk.CTkLabel(
        form_frame,
        text="Clinic License:",
        font=("Helvetica", 14),
        text_color="black"
    )  # Create a label for the clinic license
    clinic_license_label.grid(row=3, column=0, sticky="e", pady=5)  # Place the label in the grid
    clinic_license_button = ctk.CTkButton(
        form_frame,
        text="Choose File",
        font=("Helvetica", 12),
        command=lambda: choose_file(clinic_license_path_label)
    )  # Create a button to choose a file
    clinic_license_button.grid(row=3, column=1, pady=5)  # Place the button in the grid
    clinic_license_path_label = ctk.CTkLabel(
        form_frame,
        text="",
        font=("Helvetica", 12),
        text_color="black"
    )  # Create a label to display the chosen file path
    clinic_license_path_label.grid(row=4, column=0, columnspan=2, pady=5)  # Place the label in the grid

    # Function to choose a file and display the file name
    def choose_file(label):
        global clinic_license_path
        path = browse_file()  # Call the browse_file function to get the selected file path
        if path:
            clinic_license_path = path  # Store the selected file path
            label.configure(text="File uploaded successfully")  # Update the label text

    # Clinic admin info section
    clinic_admin_info_label = ctk.CTkLabel(
        form_frame,
        text="Clinic Admin info",
        font=("Helvetica", 16),
        text_color="black"
    )  # Create a label for the clinic admin info section
    clinic_admin_info_label.grid(row=5, column=0, columnspan=2, pady=5)  # Place the label in the grid

    fullname_label = ctk.CTkLabel(
        form_frame,
        text="Fullname:",
        font=("Helvetica", 14),
        text_color="black"
    )  # Create a label for the admin's full name
    fullname_label.grid(row=6, column=0, sticky="e", pady=5)  # Place the label in the grid
    fullname_entry = ctk.CTkEntry(
        form_frame,
        font=("Helvetica", 14),
        fg_color="white",
        text_color="black"
    )  # Create an entry widget for the admin's full name
    fullname_entry.grid(row=6, column=1, pady=5)  # Place the entry widget in the grid

    email_label = ctk.CTkLabel(
        form_frame,
        text="Email:",
        font=("Helvetica", 14),
        text_color="black"
    )  # Create a label for the admin's email
    email_label.grid(row=7, column=0, sticky="e", pady=5)  # Place the label in the grid
    email_entry = ctk.CTkEntry(
        form_frame,
        font=("Helvetica", 14),
        fg_color="white",
        text_color="black"
    )  # Create an entry widget for the admin's email
    email_entry.grid(row=7, column=1, pady=5)  # Place the entry widget in the grid

    username_label = ctk.CTkLabel(
        form_frame,
        text="Username:",
        font=("Helvetica", 14),
        text_color="black"
    )  # Create a label for the admin's username
    username_label.grid(row=8, column=0, sticky="e", pady=5)  # Place the label in the grid
    username_entry = ctk.CTkEntry(
        form_frame,
        font=("Helvetica", 14),
        fg_color="white",
        text_color="black"
    )  # Create an entry widget for the admin's username
    username_entry.grid(row=8, column=1, pady=5)  # Place the entry widget in the grid

    password_label = ctk.CTkLabel(
        form_frame,
        text="Password:",
        font=("Helvetica", 14),
        text_color="black"
    )  # Create a label for the admin's password
    password_label.grid(row=9, column=0, sticky="e", pady=5)  # Place the label in the grid
    password_entry = ctk.CTkEntry(
        form_frame,
        font=("Helvetica", 14),
        fg_color="white",
        text_color="black",
        show="*"
    )  # Create an entry widget for the admin's password
    password_entry.grid(row=9, column=1, pady=5)  # Place the entry widget in the grid

    confirm_password_label = ctk.CTkLabel(
        form_frame,
        text="Confirm Password:",
        font=("Helvetica", 14),
        text_color="black"
    )  # Create a label for confirming the password
    confirm_password_label.grid(row=10, column=0, sticky="e", pady=5)  # Place the label in the grid
    confirm_password_entry = ctk.CTkEntry(
        form_frame,
        font=("Helvetica", 14),
        fg_color="white",
        text_color="black",
        show="*"
    )  # Create an entry widget for confirming the password
    confirm_password_entry.grid(row=10, column=1, pady=5)  # Place the entry widget in the grid

    phone_number_label = ctk.CTkLabel(
        form_frame,
        text="Phone Number:",
        font=("Helvetica", 14),
        text_color="black"
    )  # Create a label for the admin's phone number
    phone_number_label.grid(row=11, column=0, sticky="e", pady=5)  # Place the label in the grid
    phone_number_entry = ctk.CTkEntry(
        form_frame,
        font=("Helvetica", 14),
        fg_color="white",
        text_color="black"
    )  # Create an entry widget for the admin's phone number
    phone_number_entry.grid(row=11, column=1, pady=5)  # Place the entry widget in the grid

    admin_address_label = ctk.CTkLabel(
        form_frame,
        text="Admin Address:",
        font=("Helvetica", 14),
        text_color="black"
    )  # Create a label for the admin's address
    admin_address_label.grid(row=12, column=0, sticky="e", pady=5)  # Place the label in the grid
    admin_address_entry = ctk.CTkEntry(
        form_frame,
        font=("Helvetica", 14),
        fg_color="white",
        text_color="black"
    )  # Create an entry widget for the admin's address
    admin_address_entry.grid(row=12, column=1, pady=5)  # Place the entry widget in the grid

    date_of_birth_label = ctk.CTkLabel(
        form_frame,
        text="Date of Birth:",
        font=("Helvetica", 14),
        text_color="black"
    )  # Create a label for the admin's date of birth
    date_of_birth_label.grid(row=13, column=0, sticky="e", pady=5)  # Place the label in the grid
    date_of_birth_entry = DateEntry(
        form_frame,
        font=("Helvetica", 14),
        date_pattern='y-mm-dd'
    )  # Create a date entry widget for the admin's date of birth
    date_of_birth_entry.grid(row=13, column=1, pady=5)  # Place the date entry widget in the grid

    # Function to handle the register button click
    def on_register_click():
        clinic_name = clinic_name_entry.get()  # Get the clinic name from the entry widget
        clinic_address = clinic_address_entry.get()  # Get the clinic address from the entry widget
        admin_fullname = fullname_entry.get()  # Get the admin's full name from the entry widget
        admin_username = username_entry.get()  # Get the admin's username from the entry widget
        admin_password = password_entry.get()  # Get the admin's password from the entry widget
        admin_email = email_entry.get()  # Get the admin's email from the entry widget
        admin_phone_number = phone_number_entry.get()  # Get the admin's phone number from the entry widget
        admin_address = admin_address_entry.get()  # Get the admin's address from the entry widget
        admin_date_of_birth = date_of_birth_entry.get()  # Get the admin's date of birth from the date entry widget

        # Validate that all fields are filled
        if not clinic_name or not clinic_address or not admin_fullname or not admin_username or not admin_password or not admin_email or not admin_phone_number or not admin_address:
            messagebox.showerror("Error", "All fields must be filled out.")  # Show error message if any field is empty
            return

        # Validate phone number
        if not admin_phone_number.isdigit():
            messagebox.showerror("Error", "Phone number must contain only digits.")  # Show error message if phone number is not numeric
            return

        # Validate password match
        if admin_password != confirm_password_entry.get():
            messagebox.showerror("Error", "Passwords do not match!")  # Show error message if passwords do not match
            return

        # Password strength policy
        ok, msg = check_password_policy(admin_password)
        if not ok:
            messagebox.showerror("Weak Password", msg)
            return

        # Basic email format validation
        email_pattern = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
        if not email_pattern.match(admin_email):
            messagebox.showerror("Error", "Please enter a valid email address.")
            return

        # Validate that a file was chosen
        if not clinic_license_path:
            messagebox.showerror("Error", "Please upload a clinic license file.")  # Show error message if no file is chosen
            return

        submit_clinic_data(
            clinic_name,
            clinic_address,
            clinic_license_path,
            admin_fullname,
            admin_username,
            admin_password,
            admin_email,
            admin_phone_number,
            admin_date_of_birth,
            admin_address
        )  # Submit the clinic data

    # Register button
    register_button = ctk.CTkButton(
        form_frame,
        text="Register",
        font=("Helvetica", 14),
        command=on_register_click
    )  # Create a register button
    register_button.grid(row=14, column=0, columnspan=2, pady=10)  # Place the register button in the grid

    # Back button
    def on_back_click():
        clinic_register_root.destroy()  # Destroy the current window
        import register_page  # Import the register_page module
        register_page.create_register_window()  # Open the register window

    back_button = ctk.CTkButton(
        form_frame,
        text="Back",
        font=("Helvetica", 14),
        command=on_back_click
    )  # Create a back button
    back_button.grid(row=15, column=0, columnspan=2, pady=10)  # Place the back button in the grid

    clinic_register_root.mainloop()  # Run the main loop for the registration window


if __name__ == "__main__":
    create_clinic_register_window()  # Call the function to create the clinic registration window
