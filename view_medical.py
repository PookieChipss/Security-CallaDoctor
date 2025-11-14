import customtkinter as ctk  # Importing the custom tkinter library as ctk
from tkinter import ttk  # Importing the ttk module from tkinter for themed widgets
import mysql.connector  # Importing the MySQL Connector Python module
import os  # Importing the os module
import sys  # Importing the sys module for accessing command line arguments

# Get doctor_id and patient_id from command line arguments
doctor_id = sys.argv[1] if len(sys.argv) > 1 else None
patient_id = sys.argv[2] if len(sys.argv) > 2 else None

# Database connection details
db_config = {
    'user': 'root',
    'password': 'calladoctor1234',
    'host': 'localhost',
    'database': 'calladoctor'
}

def fetch_medical_records(patient_id):
    """Fetch medical records for a specific patient."""
    try:
        connection = mysql.connector.connect(**db_config)  # Establishing connection to MySQL database
        cursor = connection.cursor()  # Creating a cursor object

        # Query to fetch medical records for the specified patient
        cursor.execute("""
            SELECT a.appointment_date, a.appointment_time, c.clinic_name, d.fullname, pr.medical_report
            FROM prescriptions pr
            JOIN appointments a ON pr.appointment_id = a.appointment_id
            JOIN clinics c ON a.clinic_id = c.clinic_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s
            ORDER BY a.appointment_date DESC
        """, (patient_id,))
        records = cursor.fetchall()  # Fetching all records

        cursor.close()  # Closing the cursor
        connection.close()  # Closing the database connection

        return records  # Returning fetched records
    except mysql.connector.Error as e:
        print(f"Database error: {e}")  # Printing error message if any
        return []  # Returning empty list if error occurs

def back_action():
    """Go back to the doctor home page."""
    root.destroy()  # Destroying the main window
    os.system(f'python doctorhome.py {doctor_id}')  # Running the doctor home page script

# Create main window
ctk.set_appearance_mode("light")  # Setting appearance mode to light
ctk.set_default_color_theme("blue")  # Setting default color theme to blue

root = ctk.CTk()  # Creating the main tkinter window
root.title("Medical Record")  # Setting window title
root.geometry("800x600")  # Setting window dimensions
root.configure(fg_color="white")  # Configuring the foreground color to white

main_frame = ctk.CTkFrame(root, fg_color="white")  # Creating the main frame with white background
main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)  # Packing the main frame with padding

record_frame = ctk.CTkFrame(main_frame, fg_color="lightblue", corner_radius=10)  # Creating the record frame with light blue background
record_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)  # Packing the record frame with padding

title_label = ctk.CTkLabel(record_frame, text="MEDICAL RECORD", fg_color="lightblue", font=("Arial", 18))  # Creating the title label for medical record
title_label.pack(fill=ctk.X, pady=(0, 10))  # Packing the title label with padding

# Style for Treeview
style = ttk.Style()  # Creating a ttk Style object
style.configure("Treeview.Heading", font=("Arial", 14, "bold"))  # Configuring style for headings in Treeview
style.configure("Treeview", font=("Arial", 12), rowheight=25)  # Configuring style for Treeview

# Creating Treeview widget for displaying medical records
record_tree = ttk.Treeview(record_frame, columns=("date", "time", "clinic", "doctor", "prescriptions"), show='headings')
record_tree.heading("date", text="Date Treated")  # Adding heading for the date column
record_tree.heading("time", text="Time Treated")  # Adding heading for the time column
record_tree.heading("clinic", text="Treated at Clinic")  # Adding heading for the clinic column
record_tree.heading("doctor", text="Treated by Doctor")  # Adding heading for the doctor column
record_tree.heading("prescriptions", text="Prescriptions")  # Adding heading for the prescriptions column
record_tree.pack(fill=ctk.BOTH, expand=True)  # Packing the Treeview widget

for col in ("date", "time", "clinic", "doctor", "prescriptions"):
    record_tree.column(col, anchor="center", width=100, stretch=ctk.YES)  # Configuring columns in the Treeview

# Fetch medical records for the specific patient
records = fetch_medical_records(patient_id)

# Inserting data into the medical record Treeview
for record in records:
    record_tree.insert("", "end", values=record)  # Inserting each record into the Treeview

# Button to go back to the doctor home page
back_button = ctk.CTkButton(main_frame, text="Back", command=back_action, fg_color="#4BAAC8", text_color="white", font=("Arial", 12))
back_button.pack(pady=10)  # Packing the back button with padding

root.mainloop()  # Running the main loop to display the window