import customtkinter as ctk  # Importing the custom tkinter library as ctk
from tkinter import ttk  # Importing the ttk module from tkinter for themed widgets
import mysql.connector  # Importing the MySQL Connector Python module
import os  # Importing the os module
import sys  # Importing the sys module for accessing command line arguments

# Get patient_id and patient's full name from command line arguments
if len(sys.argv) > 2:
    patient_id = int(sys.argv[1])  # Extracting patient_id from command line argument
    patient_fullname = sys.argv[2]  # Extracting patient_fullname from command line argument
else:
    patient_id = 1  # Default patient_id if not provided
    patient_fullname = "PATIENT"  # Default patient_fullname if not provided

# Database connection details
db_config = {
    'user': 'root',
    'password': 'calladoctor1234',
    'host': 'localhost',
    'database': 'calladoctor'
}

def fetch_appointments(patient_id):
    try:
        connection = mysql.connector.connect(**db_config)  # Establishing connection to MySQL database
        cursor = connection.cursor()  # Creating a cursor object

        # Fetch past appointments
        cursor.execute("""
            SELECT a.appointment_date, a.appointment_time, a.reason, d.fullname AS doctor_name, c.clinic_name, IFNULL(pr.medical_report, 'N/A')
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            JOIN clinics c ON a.clinic_id = c.clinic_id
            LEFT JOIN prescriptions pr ON a.appointment_id = pr.appointment_id
            WHERE a.patient_id = %s AND a.treatment_status = 'done'
            ORDER BY a.appointment_date DESC
        """, (patient_id,))
        past_appointments = cursor.fetchall()  # Fetching all past appointments

        # Fetch upcoming appointments
        cursor.execute("""
            SELECT a.appointment_date, a.appointment_time, a.reason, d.fullname AS doctor_name, c.clinic_name, 'N/A' AS prescriptions
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            JOIN clinics c ON a.clinic_id = c.clinic_id
            WHERE a.patient_id = %s AND a.treatment_status = 'pending' AND a.appointment_request_status = 'accepted'
            ORDER BY a.appointment_date ASC
        """, (patient_id,))
        upcoming_appointments = cursor.fetchall()  # Fetching all upcoming appointments

        cursor.close()  # Closing the cursor
        connection.close()  # Closing the database connection

        return past_appointments, upcoming_appointments  # Returning fetched appointments
    except mysql.connector.Error as e:
        print(f"The error '{e}' occurred")  # Printing error message
        return [], []  # Returning empty lists if error occurs

def back_action():
    root.destroy()  # Destroying the main window
    os.system(f'python "C:/Users/user/Documents/GitHub/SoftwareEng/Software_Project/Harvind/patienthome.py" {patient_id} {patient_fullname}')  # Opening patient home page

# Create main window
ctk.set_appearance_mode("light")  # Setting appearance mode to light
ctk.set_default_color_theme("blue")  # Setting default color theme to blue

root = ctk.CTk()  # Creating the main tkinter window
root.title("Appointment System")  # Setting window title
root.geometry("800x700")  # Setting window dimensions
root.configure(fg_color="white")  # Configuring foreground color

main_frame = ctk.CTkFrame(root, fg_color="white")  # Creating the main frame
main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)  # Packing the main frame

history_frame = ctk.CTkFrame(main_frame, fg_color="lightblue", corner_radius=10)  # Creating the history frame
history_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)  # Packing the history frame

past_appointments_label = ctk.CTkLabel(history_frame, text="PAST APPOINTMENTS", fg_color="lightblue", font=("Arial", 18))  # Creating the label for past appointments
past_appointments_label.pack(fill=ctk.X, pady=(0, 10))  # Packing the past appointments label

# Style for the Treeview
style = ttk.Style()  # Creating a ttk Style object
style.configure("Treeview.Heading", font=("Arial", 14, "bold"))  # Configuring style for headings in Treeview
style.configure("Treeview", font=("Arial", 12), rowheight=25)  # Configuring style for Treeview

# Creating Treeview widget for past appointments
past_appointments_tree = ttk.Treeview(history_frame, columns=("date", "time", "reason", "doctor", "clinic", "prescriptions"), show='headings')
past_appointments_tree.heading("date", text="Date")  # Adding heading for date column
past_appointments_tree.heading("time", text="Time")  # Adding heading for time column
past_appointments_tree.heading("reason", text="Reason")  # Adding heading for reason column
past_appointments_tree.heading("doctor", text="Doctor")  # Adding heading for doctor column
past_appointments_tree.heading("clinic", text="Clinic")  # Adding heading for clinic column
past_appointments_tree.heading("prescriptions", text="Prescriptions")  # Adding heading for prescriptions column
past_appointments_tree.pack(fill=ctk.BOTH, expand=True)  # Packing the past appointments Treeview

for col in ("date", "time", "reason", "doctor", "clinic", "prescriptions"):
    past_appointments_tree.column(col, anchor="center", width=100, stretch=ctk.YES)  # Configuring columns

upcoming_appointments_label = ctk.CTkLabel(history_frame, text="UPCOMING APPOINTMENTS", fg_color="lightblue", font=("Arial", 18))  # Creating the label for upcoming appointments
upcoming_appointments_label.pack(fill=ctk.X, pady=(10, 0))  # Packing the upcoming appointments label

# Creating Treeview widget for upcoming appointments
upcoming_appointments_tree = ttk.Treeview(history_frame, columns=("date", "time", "reason", "doctor", "clinic"), show='headings')
upcoming_appointments_tree.heading("date", text="Date")  # Adding heading for date column
upcoming_appointments_tree.heading("time", text="Time")  # Adding heading for time column
upcoming_appointments_tree.heading("reason", text="Reason")  # Adding heading for reason column
upcoming_appointments_tree.heading("doctor", text="Doctor")  # Adding heading for doctor column
upcoming_appointments_tree.heading("clinic", text="Clinic")  # Adding heading for clinic column
upcoming_appointments_tree.pack(fill=ctk.BOTH, expand=True)  # Packing the upcoming appointments Treeview

for col in ("date", "time", "reason", "doctor", "clinic"):
    upcoming_appointments_tree.column(col, anchor="center", width=100, stretch=ctk.YES)  # Configuring columns

# Fetch appointment data for the specific patient
past_appointments, upcoming_appointments = fetch_appointments(patient_id)

# Inserting data into the past appointments Treeview
for appointment in past_appointments:
    past_appointments_tree.insert("", "end", values=appointment)

# Inserting data into the upcoming appointments Treeview
for appointment in upcoming_appointments:
    upcoming_appointments_tree.insert("", "end", values=appointment)

# Button to go back to patient home page
back_button = ctk.CTkButton(main_frame, text="Back", command=back_action, fg_color="#4BAAC8", text_color="white", font=("Arial", 12))
back_button.pack(pady=10)  # Packing the back button

root.mainloop()  # Running the main loop