import customtkinter as ctk  # Import customtkinter for creating custom UI elements
from tkinter import messagebox  # Import messagebox for showing dialog boxes
from tkinter import ttk  # Import ttk for using Combobox
import mysql.connector  # Import mysql.connector for database connectivity
import os  # Import os for running external scripts
import sys  # Import sys for handling command line arguments
import os as _os
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

    salt = _os.urandom(SALT_SIZE)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return base64.b64encode(salt + dk).decode("utf-8")


def check_password_policy(password: str):
    """
    Basic password strength policy for doctor accounts:
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


# Get clinic ID and the admin full name from command line arguments
if len(sys.argv) > 2:
    clinic_id = sys.argv[1]
    admin_fullname = ' '.join(sys.argv[2:])
else:
    clinic_id = None
    admin_fullname = "ADMIN"

# Debug: Print received command-line arguments
print(f"Debug: Received clinic_id = {clinic_id}, admin_fullname = {admin_fullname}")


# Function to validate and save the new doctor's information in the database
def save_doctor():
    fullname = fullname_entry.get().strip()
    username = username_entry.get().strip()
    password = password_entry.get()
    confirm_password = confirm_password_entry.get()
    gender = gender_combobox.get()
    ic = ic_entry.get().strip()
    email = email_entry.get().strip()
    phone = phone_entry.get().strip()
    address = address_entry.get().strip()
    year = year_combobox.get()
    month = month_combobox.get()
    day = day_combobox.get()

    # Validate that all fields are filled
    if not (fullname and username and password and confirm_password and gender and ic and email and phone and address and year and month and day):
        messagebox.showerror("Error", "Please fill all the fields.")
        return

    # Validate IC length and content
    if not ic.isdigit() or len(ic) != 12:
        messagebox.showerror("Error", "IC must contain exactly 12 digits.")
        return

    # Validate phone number
    if not phone.isdigit():
        messagebox.showerror("Error", "Phone number must contain only digits.")
        return

    # Validate date of birth
    if year == "Year":
        messagebox.showerror("Error", "Please fill in the year column.")
        return

    if month == "Month":
        messagebox.showerror("Error", "Please fill in the month column.")
        return

    if day == "Day":
        messagebox.showerror("Error", "Please fill in the day column.")
        return

    dob = f"{year}-{month}-{day}"

    # Validate passwords match
    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match.")
        return

    # Password strength policy
    ok, msg = check_password_policy(password)
    if not ok:
        messagebox.showerror("Weak Password", msg)
        return

    # Basic email format validation
    email_pattern = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
    if not email_pattern.match(email):
        messagebox.showerror("Error", "Please enter a valid email address.")
        return

    connection = None
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='calladoctor1234',
            database='calladoctor'
        )
        cursor = connection.cursor()

        # Ensure clinic_id is assigned correctly
        global clinic_id
        if clinic_id is None:
            cursor.execute('''
                SELECT admin_clinics.clinic_id 
                FROM admin_clinics 
                JOIN users ON admin_clinics.admin_id = users.user_id 
                WHERE users.fullname = %s
            ''', (admin_fullname,))
            clinic_id_result = cursor.fetchone()
            print(f"Debug: SQL query executed with admin_fullname = {admin_fullname}")  # Debug print statement
            if clinic_id_result:
                clinic_id = clinic_id_result[0]
                print(f"Debug: Retrieved clinic_id = {clinic_id}")  # Debug print statement
            else:
                messagebox.showerror("Error", "Clinic ID not found.")
                print("Debug: Clinic ID not found.")  # Debug print statement
                return

        # Check for duplicate username / email / phone for doctors
        cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists.")
            return

        cursor.execute("SELECT 1 FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Email already exists.")
            return

        cursor.execute("SELECT 1 FROM users WHERE phone_number = %s", (phone,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Phone number already exists.")
            return

        # ---- HASH PASSWORD BEFORE INSERTING (security feature) ----
        hashed_password = hash_password(password)

        # Insert new user into users table
        cursor.execute('''
            INSERT INTO users (username, password, email, phone_number, fullname, role, date_of_birth, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (username, hashed_password, email, phone, fullname, 'doctor', dob, address))
        user_id = cursor.lastrowid

        # Insert new doctor into doctors table
        cursor.execute('''
            INSERT INTO doctors (user_id, fullname, clinic_id, is_available, gender, identification_number)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (user_id, fullname, clinic_id, 1, gender, ic))
        connection.commit()
        messagebox.showinfo("Success", "Doctor added successfully!")
        root.destroy()
        os.system(f'python adminclinichome.py {clinic_id} "{admin_fullname}"')
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
    finally:
        try:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
        except Exception:
            pass


# Function to handle back action
def back_action():
    root.destroy()
    os.system(f'python adminclinichome.py {clinic_id} "{admin_fullname}"')


# Validation function for IC entry
def limit_ic_length(*args):
    value = ic_var.get()
    if len(value) > 12:
        ic_var.set(value[:12])


# Create main window
ctk.set_appearance_mode("light")  # Set appearance mode
ctk.set_default_color_theme("blue")  # Set color theme

root = ctk.CTk()
root.title("Add Doctor")
root.geometry('500x700')  # Set initial window size
root.configure(fg_color="#AED6F1")

# Title label
title_label = ctk.CTkLabel(root, text="Add Doctor", font=("Helvetica", 24, "bold"), fg_color="#AED6F1")
title_label.pack(pady=10)

# Frame for form
form_frame = ctk.CTkFrame(root, fg_color="#AED6F1")
form_frame.pack(pady=20, padx=20, fill=ctk.BOTH, expand=True)

# Configure grid layout
form_frame.grid_columnconfigure(0, weight=1)
form_frame.grid_columnconfigure(1, weight=1)
form_frame.grid_rowconfigure(list(range(10)), pad=10)  # Add padding between rows

# Form fields
labels = ["Fullname:", "Username:", "Password:", "Confirm Password:", "Gender:", "IC(without dash):", "Email:", "Phone:", "Address:", "Date of Birth:"]
entries = {}

for i, label_text in enumerate(labels):
    label = ctk.CTkLabel(form_frame, text=label_text, font=("Helvetica", 14), anchor="center")
    label.grid(row=i, column=0, sticky="e", pady=5, padx=5)
    if label_text == "Gender:":
        entry = ctk.CTkComboBox(form_frame, font=("Helvetica", 14), values=["Male", "Female"], justify="center")
        entry.set("Male")  # Set default value
        entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
        entries[label_text] = entry
    elif label_text == "Date of Birth:":
        dob_frame = ctk.CTkFrame(form_frame, fg_color="#AED6F1")
        dob_frame.grid(row=i, column=1, pady=5, padx=5, sticky="w")
        year_combobox = ttk.Combobox(dob_frame, font=("Helvetica", 14), values=[str(year) for year in range(1900, 2025)], width=4)
        year_combobox.pack(side=ctk.LEFT)
        year_combobox.set("Year")
        month_combobox = ttk.Combobox(dob_frame, font=("Helvetica", 14), values=[f"{month:02d}" for month in range(1, 13)], width=2)
        month_combobox.pack(side=ctk.LEFT, padx=(5, 0))
        month_combobox.set("Month")
        day_combobox = ttk.Combobox(dob_frame, font=("Helvetica", 14), values=[f"{day:02d}" for day in range(1, 32)], width=2)
        day_combobox.pack(side=ctk.LEFT, padx=(5, 0))
        day_combobox.set("Day")
        entries["Year"] = year_combobox
        entries["Month"] = month_combobox
        entries["Day"] = day_combobox
    else:
        entry = ctk.CTkEntry(form_frame, font=("Helvetica", 14), show="*" if "Password" in label_text else "", justify="center")
        entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
        entries[label_text] = entry

# Frame for buttons
button_frame = ctk.CTkFrame(root, fg_color="#AED6F1")
button_frame.pack(pady=10, fill=ctk.X)

# Back button
back_button = ctk.CTkButton(button_frame, text="Back", command=back_action, font=("Helvetica", 12))
back_button.pack(side=ctk.LEFT, padx=15, pady=10)

# Save button
save_button = ctk.CTkButton(button_frame, text="Save", command=save_doctor, font=("Helvetica", 12))
save_button.pack(side=ctk.RIGHT, padx=15, pady=10)

# Unpack entries for easier access
fullname_entry = entries["Fullname:"]
username_entry = entries["Username:"]
password_entry = entries["Password:"]
confirm_password_entry = entries["Confirm Password:"]
gender_combobox = entries["Gender:"]
ic_entry = entries["IC(without dash):"]
email_entry = entries["Email:"]
phone_entry = entries["Phone:"]
address_entry = entries["Address:"]

# Set up IC entry variable and trace for validation
ic_var = ctk.StringVar()
ic_var.trace_add("write", limit_ic_length)
ic_entry.configure(textvariable=ic_var)

# Add padding to form_frame to balance left and right spaces
form_frame.pack(pady=20, padx=(15, 85), fill=ctk.BOTH, expand=True)

# Force the window to render before entering the main loop
root.update_idletasks()

# Run the main loop after everything is packed
root.mainloop()
