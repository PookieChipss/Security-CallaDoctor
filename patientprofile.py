import customtkinter as ctk  # Import customtkinter module (assuming it's a custom tkinter library)
from tkinter import messagebox  # Import messagebox from tkinter for displaying messages
from PIL import Image, ImageTk  # Import Image and ImageTk from PIL library for image processing
import mysql.connector  # Import mysql.connector for MySQL database connection
from mysql.connector import Error  # Import Error class from mysql.connector
import sys  # Import sys module for accessing command line arguments
import os  # Import os module for interacting with the operating system

# Function to fetch patient details based on patient_id
def fetch_patient_details(patient_id):
    try:
        # Establish connection to MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='calladoctor1234',
            database='calladoctor'
        )
        cursor = connection.cursor()  # Create cursor object to execute SQL queries

        # Fetch patient details from the database
        cursor.execute('''
            SELECT u.fullname, u.username, p.identification_number, p.gender, u.address, u.date_of_birth, u.email, u.phone_number 
            FROM users u
            JOIN patients p ON u.user_id = p.user_id
            WHERE p.patient_id = %s
        ''', (patient_id,))
        result = cursor.fetchone()  # Fetch the first row
        return result  # Return the fetched patient details
    except Error as e:
        messagebox.showerror("Error", f"Error fetching patient details: {e}")  # Show error message box if fetching fails
    finally:
        if connection.is_connected():
            cursor.close()  # Close cursor object
            connection.close()  # Close database connection
    return None  # Return None if fetching fails

# Function to navigate back to the home screen
def back_to_home(patient_id, patient_fullname):
    root.destroy()  # Destroy the current GUI window
    os.system(f'python "C:/Users/user/Documents/GitHub/SoftwareEng/Software_Project/Harvind/patienthome.py" {patient_id} {patient_fullname}')

# Function to create patient profile window
def create_patient_profile_window(patient_id, patient_fullname):
    global root  # Use global variable for the main window

    # Set appearance mode and default color theme for GUI
    ctk.set_appearance_mode("light")  # Modes: system (default), light, dark
    ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

    root = ctk.CTk()  # Create main tkinter window object
    root.title("Patient Profile")  # Set window title
    root.geometry("550x550")  # Set window size

    # Main content area
    main_frame = ctk.CTkFrame(root, fg_color="lightblue")  # Create main frame with light blue background
    main_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=20, pady=20)  # Pack main frame

    # Fetch patient details
    patient_details = fetch_patient_details(patient_id)

    # Check if patient details were fetched successfully
    if not patient_details:
        messagebox.showerror("Error", "User details not found!")  # Show error message if details not found
        root.destroy()  # Destroy window
        return  # Exit function

    # Profile section
    profile_frame = ctk.CTkFrame(main_frame, fg_color="lightblue", corner_radius=10)  # Create profile frame with light blue background and rounded corners
    profile_frame.pack(expand=True, pady=10, ipadx=20, ipady=20)  # Pack profile frame

    profile_label = ctk.CTkLabel(profile_frame, text="PATIENT PROFILE", font=("Arial", 16, "bold"))  # Create profile label
    profile_label.grid(row=0, columnspan=2, pady=20)  # Grid profile label

    # Labels for patient details
    labels = ["Fullname:", "Username:", "IC:", "Gender:", "Address:", "Date of Birth:", "Email:", "Tel:"]

    # Iterate through labels and patient details
    for i, label_text in enumerate(labels):
        label = ctk.CTkLabel(profile_frame, text=label_text, font=("Arial", 12))  # Create label
        label.grid(row=i + 1, column=0, sticky="e", padx=5, pady=5)  # Grid label
        entry = ctk.CTkEntry(profile_frame, font=("Arial", 12))  # Create entry
        entry.grid(row=i + 1, column=1, sticky="w", padx=5, pady=5)  # Grid entry
        entry.insert(0, patient_details[i])  # Insert patient detail into entry
        entry.configure(state='readonly')  # Set entry to read-only

    # Edit profile button
    edit_button = ctk.CTkButton(profile_frame, text="Edit Profile", font=("Arial", 12),
                                command=lambda: edit_profile_action(root, patient_id, patient_fullname))  # Create edit button
    edit_button.grid(row=len(labels) + 1, columnspan=2, pady=10)  # Grid edit button

    # Back button
    back_button = ctk.CTkButton(profile_frame, text="Back", font=("Arial", 12),
                                command=lambda: back_to_home(patient_id, patient_fullname))  # Create back button
    back_button.grid(row=len(labels) + 2, columnspan=2, pady=10)  # Grid back button

    root.mainloop()  # Start main tkinter event loop

# Function to handle edit profile action
def edit_profile_action(root, patient_id, patient_fullname):
    root.destroy()  # Destroy current window
    import patienteditprofile  # Import patienteditprofile module
    patienteditprofile.create_patient_edit_profile_window(patient_id, patient_fullname)  # Call function to create edit profile window

# Main block to execute when script is run
if __name__ == "__main__":
    if len(sys.argv) > 2:
        patient_id = int(sys.argv[1])  # Extract patient_id from command line argument
        patient_fullname = sys.argv[2]  # Extract patient's full name from command line argument
    else:
        patient_id = 1  # Default patient_id for testing
        patient_fullname = "PATIENT"

    create_patient_profile_window(patient_id, patient_fullname)  # Call function to create patient profile window