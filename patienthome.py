import os  # Import os module for interacting with the operating system
import sys  # Import sys module for accessing command line arguments
import tkinter as tk  # Import tkinter module for GUI
from tkinter import messagebox  # Import messagebox from tkinter for displaying messages
from PIL import Image  # Import Image from PIL library for image processing
import mysql.connector  # Import mysql.connector for MySQL database connection
import customtkinter as ctk  # Import customtkinter module (assuming it's a custom tkinter library)

# Get patient_id and patient's full name from command line arguments
if len(sys.argv) > 2:
    patient_id = int(sys.argv[1])  # Extract patient_id from command line argument
    patient_fullname = sys.argv[2]  # Extract patient's full name from command line argument
else:
    patient_id = 1  # Default patient_id if not provided
    patient_fullname = "PATIENT"  # Default patient's full name if not provided

# Database connection details
db_config = {
    'user': 'root',  # Username for MySQL database
    'password': 'calladoctor1234',  # Password for MySQL database
    'host': 'localhost',  # Host address of MySQL server
    'database': 'calladoctor'  # Database name
}

# Function to fetch appointments based on patient_id
def fetch_appointments(patient_id):
    try:
        connection = mysql.connector.connect(**db_config)  # Connect to MySQL database using db_config
        cursor = connection.cursor()  # Create cursor object to execute SQL queries

        # Fetch approved/rejected appointments
        cursor.execute("""
            SELECT a.appointment_date, a.appointment_time, a.reason, d.fullname AS doctor_name, c.clinic_name, a.appointment_request_status
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            JOIN clinics c ON a.clinic_id = c.clinic_id
            WHERE a.patient_id = %s AND a.appointment_request_status IN ('accepted', 'rejected')
            ORDER BY a.appointment_date ASC
        """, (patient_id,))
        approved_requests = cursor.fetchall()  # Get all approved/rejected appointments

        # Fetch pending appointments
        cursor.execute("""
            SELECT a.appointment_date, a.appointment_time, a.reason, d.fullname AS doctor_name, c.clinic_name
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            JOIN clinics c ON a.clinic_id = c.clinic_id
            WHERE a.patient_id = %s AND a.appointment_request_status = 'pending'
            ORDER BY a.appointment_date ASC
        """, (patient_id,))
        pending_requests = cursor.fetchall()  # Get all pending appointments

        cursor.close()  # Close cursor
        connection.close()  # Close database connection

        return approved_requests, pending_requests  # Return both types of appointments
    except mysql.connector.Error as e:
        print(f"The error '{e}' occurred")  # Print error message if database connection or query fails
        return [], []  # Return empty lists if there's an error

# Function to refresh appointments displayed on the screen
def refresh_appointments():
    # Fetch appointments
    approved_requests, pending_requests = fetch_appointments(patient_id)

    # Clear existing widgets in approved and pending requests frames
    for widget in approved_requests_frame.winfo_children():
        widget.destroy()
    for widget in pending_requests_frame.winfo_children():
        widget.destroy()

    # Configure grid columns for approved and pending requests frames
    for col in range(6):
        approved_requests_frame.grid_columnconfigure(col, weight=1)
    for col in range(6):
        pending_requests_frame.grid_columnconfigure(col, weight=1)

    # Create headers for approved requests
    approved_columns = ["Date", "Time", "Reason", "Doctor", "Clinic", "Status"]
    for col in approved_columns:
        header = ctk.CTkLabel(approved_requests_frame, text=col, font=("Arial", 14, "bold"), fg_color="lightblue")
        header.grid(row=0, column=approved_columns.index(col), sticky="nsew")

    # Display approved requests
    for i, request in enumerate(approved_requests):
        for j, value in enumerate(request):
            label = ctk.CTkLabel(approved_requests_frame, text=value, font=("Arial", 12), fg_color="white")
            label.grid(row=i+1, column=j, sticky="nsew")

    # Create headers for pending requests
    pending_columns = ["Date", "Time", "Reason", "Doctor", "Clinic", "Action"]
    for col in pending_columns:
        header = ctk.CTkLabel(pending_requests_frame, text=col, font=("Arial", 14, "bold"), fg_color="lightblue")
        header.grid(row=0, column=pending_columns.index(col), sticky="nsew")

    # Display pending requests
    for i, request in enumerate(pending_requests):
        for j, value in enumerate(request):
            label = ctk.CTkLabel(pending_requests_frame, text=value, font=("Arial", 12), fg_color="white")
            label.grid(row=i+1, column=j, sticky="nsew")

        # Add delete button for pending requests
        delete_button = ctk.CTkButton(pending_requests_frame, text="Delete", command=lambda req=request: confirm_delete_appointment(req[0]), fg_color="red", text_color="white", font=("Arial", 10))
        delete_button.grid(row=i+1, column=len(request), sticky="nsew")
        pending_requests_frame.grid_columnconfigure(len(request), weight=1)

# Function to confirm appointment deletion
def confirm_delete_appointment(appointment_date):
    response = messagebox.askyesno("Delete Confirmation", "Do you want to delete this appointment?")
    if response:
        delete_appointment(appointment_date)

# Function to delete appointment from database
def delete_appointment(appointment_date):
    try:
        connection = mysql.connector.connect(**db_config)  # Connect to MySQL database using db_config
        cursor = connection.cursor()  # Create cursor object to execute SQL queries
        # Update appointment status to 'cancelled'
        cursor.execute("""
            UPDATE appointments
            SET appointment_request_status = 'cancelled'
            WHERE patient_id = %s AND appointment_date = %s
        """, (patient_id, appointment_date))
        connection.commit()  # Commit the transaction
        cursor.close()  # Close the cursor
        connection.close()  # Close database connection
        messagebox.showinfo("Success", "Appointment request cancelled successfully!")  # Show success message
        refresh_appointments()  # Refresh appointments displayed on the screen
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Failed to cancel the appointment request: {e}")  # Show error message if update fails

# Action functions for menu buttons

# Action function for booking appointment
def appointment_book_action():
    root.destroy()  # Close the main window
    # Launch the booking appointment script with patient_id and patient_fullname as arguments
    os.system(f'python "C:/Users/user/Documents/GitHub/SoftwareEng/Software_Project/Harvind/request_appointment_patient.py" {patient_id} {patient_fullname}')

# Action function for viewing profile
def profile_action():
    root.destroy()  # Close the main window
    # Launch the patient profile script with patient_id and patient_fullname as arguments
    os.system(f'python "C:/Users/user/Documents/GitHub/SoftwareEng/Software_Project/Harvind/patientprofile.py" {patient_id} {patient_fullname}')

# Action function for viewing appointment summary
def appointment_summary_action():
    root.destroy()  # Close the main window
    # Launch the appointment summary script with patient_id and patient_fullname as arguments
    os.system(f'python "C:/Users/user/Documents/GitHub/SoftwareEng/Software_Project/Harvind/patient_appointmentsummary.py" {patient_id} {patient_fullname}')

# Action function for logging out
def logout_action():
    response = messagebox.askyesno("Logout", "Are you sure you want to logout?")  # Ask for confirmation
    if response:
        root.destroy()  # Close the main window
        os.system('python "C:/Users/user/Documents/GitHub/SoftwareEng/Software_Project/Harvind/main_page.py"')  # Launch main page script

# Initialize main window
ctk.set_appearance_mode("light")  # Set appearance mode of customtkinter to light
ctk.set_default_color_theme("blue")  # Set default color theme of customtkinter to blue

root = ctk.CTk()  # Create main tkinter window using customtkinter
root.title("Appointment System")  # Set window title
root.geometry("1000x700")  # Set window size
root.configure(fg_color="#AED6F1")  # Set main window background color

# Image file path
image_path = "C:/Users/user/Documents/GitHub/SoftwareEng/Software_Project/Harvind/Images/"

# Function to load and resize images
def load_image(image_name, size):
    img = Image.open(image_path + image_name)  # Open image file
    img = img.resize(size, Image.Resampling.LANCZOS)  # Resize image
    return ctk.CTkImage(light_image=img, size=size)  # Return custom tkinter image object

# Load images with specified size
button_size = (40, 40)  # Set button size
appointment_book_img = load_image("search.png", button_size)  # Load book appointment image
profile_img = load_image("profile.png", button_size)  # Load profile image
appointment_summary_img = load_image("appointment.png", button_size)  # Load appointment summary image
logout_img = load_image("logout.png", button_size)  # Load logout image

# Left side menu
menu_frame = ctk.CTkFrame(root, fg_color="#E6E6FA")  # Create frame for left side menu
menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)  # Pack frame to the left side, fill Y direction, and add padding

# Function to create menu button with image and text
def create_button(frame, image, text, command):
    button_frame = ctk.CTkFrame(frame, fg_color="#E6E6FA")  # Create frame for button
    button_frame.pack(fill=tk.X, pady=5, padx=5)  # Pack frame, fill X direction, and add padding
    btn = ctk.CTkButton(button_frame, image=image, command=command, fg_color="white", hover_color="#AED6F1", text="")  # Create button with image
    btn.pack(pady=0)  # Pack button with no padding
    label = ctk.CTkLabel(button_frame, text=text, fg_color="#E6E6FA", font=("Arial", 12, "bold"))  # Create label for button text
    label.pack(pady=5)  # Pack label with padding
    return button_frame  # Return button frame

# Create menu buttons
create_button(menu_frame, appointment_book_img, "BOOK APPOINTMENT", appointment_book_action)
create_button(menu_frame, profile_img, "PROFILE", profile_action)
create_button(menu_frame, appointment_summary_img, "APPOINTMENT SUMMARY", appointment_summary_action)

# Logout button at the bottom of the menu
logout_frame = ctk.CTkFrame(menu_frame, fg_color="#E6E6FA")  # Create frame for logout button
logout_frame.pack(fill=tk.X, pady=5, padx=5)  # Pack frame, fill X direction, and add padding
logout_btn = ctk.CTkButton(logout_frame, image=logout_img, command=logout_action, fg_color="white", hover_color="#AED6F1", text="")  # Create logout button with image
logout_btn.pack(pady=0)  # Pack button with no padding
logout_label = ctk.CTkLabel(logout_frame, text="LOGOUT", fg_color="#E6E6FA", font=("Arial", 12, "bold"))  # Create label for logout button text
logout_label.pack(pady=5)  # Pack label with padding

# Main content area
main_frame = ctk.CTkFrame(root, fg_color="#AED6F1")  # Create frame for main content
main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)  # Pack frame to the right side, fill both directions, and expand

# Welcome text
welcome_label = ctk.CTkLabel(main_frame, text=f"Welcome {patient_fullname}", font=("Arial", 24), fg_color="#AED6F1")  # Create welcome label
welcome_label.pack(pady=20)  # Pack label with padding

# Approved/Rejected Requests
approved_requests_label = ctk.CTkLabel(main_frame, text="APPROVED/REJECTED APPOINTMENT REQUESTS", fg_color="lightblue", font=("Arial", 18))  # Create label for approved/rejected requests
approved_requests_label.pack(fill=tk.X, pady=(0, 10))  # Pack label with padding

approved_requests_frame = ctk.CTkFrame(main_frame, fg_color="white")  # Create frame for approved requests
approved_requests_frame.pack(fill=tk.BOTH, expand=True)  # Pack frame, fill both directions, and expand

# Pending Requests
pending_requests_label = ctk.CTkLabel(main_frame, text="PENDING APPOINTMENT REQUESTS", fg_color="lightblue", font=("Arial", 18))  # Create label for pending requests
pending_requests_label.pack(fill=tk.X, pady=(10, 0))  # Pack label with padding

pending_requests_frame = ctk.CTkFrame(main_frame, fg_color="white")  # Create frame for pending requests
pending_requests_frame.pack(fill=tk.BOTH, expand=True)  # Pack frame, fill both directions, and expand

refresh_appointments()  # Refresh appointments displayed on the screen
root.mainloop()  # Start the main tkinter event loop