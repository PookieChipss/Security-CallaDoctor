import tkinter as tk  # Import tkinter library
from tkinter import messagebox, ttk  # Import messagebox and ttk modules from tkinter
from tkcalendar import Calendar  # Import Calendar widget from tkcalendar library
from datetime import datetime  # Import datetime module for date and time operations
import mysql.connector  # Import mysql.connector library for MySQL database connection
from mysql.connector import Error  # Import Error class from mysql.connector library
import subprocess  # Import subprocess module for executing external commands
import sys  # Import sys module for system-specific parameters and functions
import customtkinter as ctk  # Import customtkinter library

# Ensure command line arguments are properly passed
if len(sys.argv) > 2:
    patient_id = int(sys.argv[1])  # Get patient_id from command line argument
    patient_fullname = sys.argv[2]  # Get patient_fullname from command line argument
else:
    patient_id = 1  # Default patient_id
    patient_fullname = "PATIENT"  # Default patient_fullname

# Database connection details
db_config = {
    'user': 'root',  # Database username
    'password': 'calladoctor1234',  # Database password
    'host': 'localhost',  # Database host
    'database': 'calladoctor'  # Database name
}

def fetch_clinics():
    """Fetches clinics from the database."""
    try:
        connection = mysql.connector.connect(**db_config)  # Connect to the database using db_config
        cursor = connection.cursor()  # Create a cursor object using the connection
        cursor.execute("SELECT clinic_id, clinic_name FROM clinics WHERE is_approved = 1")  # Execute SQL query to fetch clinics
        clinics = cursor.fetchall()  # Fetch all clinics
        cursor.close()  # Close the cursor
        connection.close()  # Close the database connection
        return {clinic_name: clinic_id for clinic_id, clinic_name in clinics}  # Return dictionary of clinics
    except Error as e:
        print(f"The error '{e}' occurred")  # Print error message
        return {}  # Return an empty dictionary on error

def fetch_doctors(clinic_id):
    """Fetches doctors based on the selected clinic."""
    try:
        connection = mysql.connector.connect(**db_config)  # Connect to the database using db_config
        cursor = connection.cursor()  # Create a cursor object using the connection
        cursor.execute("SELECT doctor_id, fullname FROM doctors WHERE clinic_id = %s", (clinic_id,))  # Execute SQL query with parameters
        doctors = cursor.fetchall()  # Fetch all doctors
        cursor.close()  # Close the cursor
        connection.close()  # Close the database connection
        return doctors  # Return list of doctors
    except Error as e:
        print(f"The error '{e}' occurred")  # Print error message
        return []  # Return an empty list on error

def on_clinic_select(event):
    """Handles the event when a clinic is selected."""
    selected_clinic_name = clinic_var.get()  # Get selected clinic name
    selected_clinic_id = clinics[selected_clinic_name]  # Get clinic_id for selected clinic_name from clinics dictionary
    doctors = fetch_doctors(selected_clinic_id)  # Fetch doctors for selected clinic_id
    doctor_var.set('')  # Clear current selection in doctor_var
    doctor_menu['values'] = [doctor_name for doctor_id, doctor_name in doctors]  # Update doctor_menu with new values
    doctor_dict.clear()  # Clear doctor_dict
    doctor_dict.update({doctor_name: doctor_id for doctor_id, doctor_name in doctors})  # Update doctor_dict with new values


def send_appointment_request():
    """Sends the appointment request to the database."""
    clinic_name = clinic_var.get()  # Get selected clinic name
    clinic_id = clinics.get(clinic_name)  # Get clinic_id for selected clinic_name from clinics dictionary
    doctor_name = doctor_var.get()  # Get selected doctor name
    doctor_id = doctor_dict.get(doctor_name)  # Get doctor_id for selected doctor_name from doctor_dict dictionary
    reason = reason_entry.get("1.0", tk.END).strip()  # Get reason for appointment
    date = cal.get_date()  # Get selected date
    hour = hour_var.get()  # Get selected hour
    minute = minute_var.get()  # Get selected minute
    time = f"{hour}:{minute}"  # Format selected time as "hour:minute"

    # Validation
    if not clinic_id:
        messagebox.showerror("Error", "Please select a clinic.")  # Show error message if clinic not selected
        return

    if not doctor_id:
        messagebox.showerror("Error", "Please select a doctor.")  # Show error message if doctor not selected
        return

    if not reason:
        messagebox.showerror("Error", "Please provide a reason for the appointment.")  # Show error message if reason not provided
        return

    if not date:
        messagebox.showerror("Error", "Please select a date for the appointment.")  # Show error message if date not selected
        return

    if not hour or not minute:
        messagebox.showerror("Error", "Please select a time for the appointment.")  # Show error message if time not selected
        return

    # Convert date format from 'mm/dd/yy' to 'yyyy-mm-dd'
    date_obj = datetime.strptime(date, '%m/%d/%y')  # Parse date string to datetime object
    formatted_date = date_obj.strftime('%Y-%m-%d')  # Format datetime object as string 'yyyy-mm-dd'

    try:
        connection = mysql.connector.connect(**db_config)  # Connect to the database using db_config
        cursor = connection.cursor()  # Create a cursor object using the connection
        cursor.execute("""
            INSERT INTO appointments (clinic_id, doctor_id, patient_id, appointment_date, appointment_time, reason, appointment_request_status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
        """, (clinic_id, doctor_id, patient_id, formatted_date, time, reason))  # Execute SQL query with parameters
        connection.commit()  # Commit transaction
        cursor.close()  # Close the cursor
        connection.close()  # Close the database connection
        messagebox.showinfo("Success", "Appointment request sent successfully!")  # Show success message
        go_back_to_patient_home()  # Go back to patient home after sending the request
    except Error as e:
        messagebox.showerror("Error", f"Failed to send appointment request: {e}")  # Show error message on exception

def go_back_to_patient_home():
    """Goes back to the patient home screen."""
    root.destroy()  # Destroy the main window
    subprocess.run(['python', 'patienthome.py', str(patient_id), patient_fullname])  # Run patienthome.py script with arguments

# Create main window
root = tk.Tk()  # Create main Tkinter window
root.title("Request Appointment")  # Set window title
root.geometry("600x630")  # Set window size

clinics = fetch_clinics()  # Fetch clinics from database
doctor_dict = {}  # Initialize empty dictionary for doctors

# Clinic dropdown
clinic_label = tk.Label(root, text="Clinics Available:")  # Create label for clinics
clinic_label.pack(pady=5)  # Pack label to window
clinic_var = tk.StringVar()  # Create variable to hold selected clinic
clinic_menu = ttk.Combobox(root, textvariable=clinic_var, width=50)  # Create dropdown menu for clinics
clinic_menu['values'] = list(clinics.keys())  # Set values for dropdown menu
clinic_menu.bind("<<ComboboxSelected>>", on_clinic_select)  # Bind event handler for clinic selection
clinic_menu.pack(pady=5)  # Pack dropdown menu to window

# Doctor dropdown
doctor_label = tk.Label(root, text="Doctors:")  # Create label for doctors
doctor_label.pack(pady=5)  # Pack label to window
doctor_var = tk.StringVar()  # Create variable to hold selected doctor
doctor_menu = ttk.Combobox(root, textvariable=doctor_var, width=50)  # Create dropdown menu for doctors
doctor_menu.pack(pady=5)  # Pack dropdown menu to window

# Reason text box
reason_label = tk.Label(root, text="Reason:")  # Create label for reason
reason_label.pack(pady=5)  # Pack label to window
reason_entry = tk.Text(root, height=4, width=50)  # Create  the text box for reason
reason_entry.pack(pady=5)  # Pack text box to window

# Date picker
date_label = tk.Label(root, text="Date:")  # Create label for date
date_label.pack(pady=5)  # Pack label to window
cal = Calendar(root, selectmode='day', year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)  # Create calendar widget
cal.pack(pady=5)  # Pack calendar widget to window

# Time picker
time_label = tk.Label(root, text="Select Time:")  # Create label for time
time_label.pack(pady=5)  # Pack label to window

time_frame = tk.Frame(root)  # Create frame for time
time_frame.pack(pady=5)  # Pack frame to window

hour_var = tk.StringVar()  # Create variable to hold selected hour
hour_menu = ttk.Combobox(time_frame, textvariable=hour_var, width=3)  # Create dropdown menu for hours
hour_menu['values'] = [f"{hour:02d}" for hour in range(9, 18)]  # Set values for dropdown menu
hour_menu.pack(side=tk.LEFT, padx=5)  # Pack dropdown menu to window

minute_var = tk.StringVar()  # Create variable to hold selected minute
minute_menu = ttk.Combobox(time_frame, textvariable=minute_var, width=3)  # Create dropdown menu for minutes
minute_menu['values'] = ["00", "15", "30", "45"]  # Set values for dropdown menu
minute_menu.pack(side=tk.LEFT, padx=5)  # Pack dropdown menu to window

# Send appointment request button
send_request_button = ctk.CTkButton(root, text="Send appointment request", command=send_appointment_request)  # Create custom button for sending request
send_request_button.pack(pady=10)  # Pack button to window

# Back button
back_button = ctk.CTkButton(root, text="Back", command=go_back_to_patient_home)  # Create custom button for going back
back_button.pack(pady=5)  # Pack button to window

root.mainloop()  # Run main loop