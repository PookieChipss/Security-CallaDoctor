import customtkinter as ctk  # Importing the customtkinter library as ctk for custom themed widgets
from tkinter import messagebox, ttk  # Importing messagebox and ttk modules from tkinter
from PIL import Image, ImageTk  # Importing Image and ImageTk from PIL for handling images
import mysql.connector  # Importing the MySQL Connector Python module
import os  # Importing the os module for interacting with the operating system
import sys  # Importing the sys module for accessing command line arguments
import subprocess  # Importing subprocess module for running external processes


# Function to fetch doctor's full name
def get_doctor_fullname(doctor_id):
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="calladoctor1234",
            database="calladoctor"
        )
        cursor = db.cursor()  # Creating a cursor object to interact with the database
        cursor.execute("SELECT fullname FROM doctors WHERE doctor_id = %s", (doctor_id,))
        result = cursor.fetchone()  # Fetching one result from the executed query
        db.close()  # Closing the database connection
        if result:
            return result[0]  # Returning the doctor's full name
        else:
            raise ValueError(f"No doctor found with ID {doctor_id}")
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        messagebox.showerror("Database Error", f"Error: {err}")
        return "Doctor"


# Function to fetch patient ID based on appointment ID
def get_patient_id(appointment_id):
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="calladoctor1234",
            database="calladoctor"
        )
        cursor = db.cursor()  # Creating a cursor object to interact with the database
        cursor.execute("SELECT patient_id FROM appointments WHERE appointment_id = %s", (appointment_id,))
        result = cursor.fetchone()  # Fetching one result from the executed query
        db.close()  # Closing the database connection
        if result:
            return result[0]  # Returning the patient ID
        else:
            raise ValueError(f"No patient found for appointment ID {appointment_id}")
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        messagebox.showerror("Database Error", f"Error: {err}")
        return None


# Function to fetch appointments
def fetch_appointments(doctor_id):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="calladoctor1234",
            database="calladoctor"
        )
        cursor = connection.cursor()  # Creating a cursor object to interact with the database

        # Fetch past appointments
        cursor.execute("""
            SELECT a.appointment_date, a.appointment_time, p.fullname, a.reason, IFNULL(pr.medical_report, 'N/A')
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN prescriptions pr ON a.appointment_id = pr.appointment_id
            WHERE a.doctor_id = %s AND a.treatment_status = 'done'
            ORDER BY a.appointment_date DESC
        """, (doctor_id,))
        past_appointments = cursor.fetchall()  # Fetching all past appointments

        # Fetch upcoming appointments
        cursor.execute("""
            SELECT a.appointment_id, a.appointment_date, a.appointment_time, p.fullname, a.reason
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE a.doctor_id = %s AND a.treatment_status = 'pending' AND a.appointment_request_status = 'accepted'
            ORDER BY a.appointment_date ASC
        """, (doctor_id,))
        upcoming_appointments = cursor.fetchall()  # Fetching all upcoming appointments

        cursor.close()  # Closing the cursor
        connection.close()  # Closing the database connection

        return past_appointments, upcoming_appointments  # Returning the fetched appointments
    except mysql.connector.Error as e:
        print(f"The error '{e}' occurred")
        return [], []  # Returning empty lists if an error occurs


# Function to create prescription form and save the prescription
def create_prescription_form(appointment_id, doctor_id, patient_name):
    def save_prescription():
        prescription = text.get("1.0", ctk.END).strip()  # Getting the text from the textbox
        if prescription:
            response = messagebox.askyesno("Confirmation",
                                           "This will result in completing the patient's appointment. Do you want to proceed?")
            if response:
                try:
                    connection = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="calladoctor1234",
                        database="calladoctor"
                    )
                    cursor = connection.cursor()  # Creating a cursor object to interact with the database
                    cursor.execute("""
                        INSERT INTO prescriptions (appointment_id, doctor_id, patient_id, medical_report)
                        VALUES (%s, %s, (SELECT patient_id FROM appointments WHERE appointment_id = %s), %s)
                    """, (appointment_id, doctor_id, appointment_id, prescription))
                    cursor.execute("""
                        UPDATE appointments
                        SET treatment_status = 'done'
                        WHERE appointment_id = %s
                    """, (appointment_id,))
                    connection.commit()  # Committing the transaction
                    cursor.close()  # Closing the cursor
                    connection.close()  # Closing the database connection
                    refresh_appointments()
                    messagebox.showinfo("Success", "Prescription saved successfully.")
                    prescription_window.destroy()
                    root.deiconify()  # Re-enable the main window
                except mysql.connector.Error as err:
                    print(f"Database Error: {err}")
                    messagebox.showerror("Database Error", f"Error: {err}")
        else:
            messagebox.showwarning("Warning", "Prescription cannot be empty.")

    def go_back():
        prescription_window.destroy()
        root.deiconify()  # Re-enable the main window

    root.withdraw()  # Disable the main window

    prescription_window = ctk.CTkToplevel(root)  # Creating a new window for the prescription form
    prescription_window.title("Prescription")  # Setting the title of the window
    prescription_window.geometry("400x250")  # Setting the size of the window

    label = ctk.CTkLabel(prescription_window,
                         text=f"Enter Prescription for {patient_name}:")  # Creating a label for the textbox
    label.pack(pady=10)  # Packing the label with padding
    text = ctk.CTkTextbox(prescription_window, height=110, width=290)  # Creating a textbox for the prescription
    text.pack(pady=10)  # Packing textbox with padding

    button_frame = ctk.CTkFrame(prescription_window)  # Creating a frame for the buttons
    button_frame.pack(pady=10)  # Packing the frame with padding

    save_button = ctk.CTkButton(button_frame, text="Save", command=save_prescription)  # Creating a save button
    save_button.pack(side=ctk.LEFT, padx=5)  # Packing the save button with padding

    back_button = ctk.CTkButton(button_frame, text="Back", command=go_back)  # Creating a back button
    back_button.pack(side=ctk.LEFT, padx=5)  # Packing the back button with padding


# Function to view medical records
def view_medical_record(appointment_id, patient_name):
    patient_id = get_patient_id(appointment_id)  # Fetching the patient ID based on the appointment ID
    if patient_id:
        root.destroy()  # Destroying the main window
        subprocess.run(
            ['python', 'view_medical.py', str(doctor_id), str(patient_id)])  # Running the view_medical.py script


# Function for the button actions
def profile_action():
    root.destroy()  # Destroying the main window
    subprocess.run(['python', 'doctorprofile.py', str(doctor_id)])  # Running the doctorprofile.py script


def logout_action():
    response = messagebox.askyesno("Logout", "Are you sure you want to logout?")  # Asking for confirmation to logout
    if response:
        root.destroy()  # Destroying the main window
        os.system(
            'python "C:/Users/user/Documents/GitHub/SoftwareEng/Software_Project/Harvind/main_page.py"')  # Running the main_page.py script


# Function to refresh the appointments table
def refresh_appointments():
    past_appointments, upcoming_appointments = fetch_appointments(doctor_id)  # Fetching the appointments

    for widget in past_appointments_frame.winfo_children():  # Removing all widgets in the past appointments frame
        widget.destroy()
    for widget in upcoming_appointments_frame.winfo_children():  # Removing all widgets in the upcoming appointments frame
        widget.destroy()

    past_columns = ["Date", "Time", "Patient Name", "Reason", "Prescription"]
    for col in past_columns:
        header = ctk.CTkLabel(past_appointments_frame, text=col, font=("Arial", 14, "bold"), fg_color="#E0F7FA", padx=5,
                              pady=5)
        header.grid(row=0, column=past_columns.index(col),
                    sticky="nsew")  # Creating and placing headers for past appointments

    for i, appointment in enumerate(past_appointments):
        for j, value in enumerate(appointment):
            label = ctk.CTkLabel(past_appointments_frame, text=value, font=("Arial", 12), fg_color="white", padx=5,
                                 pady=5)
            label.grid(row=i + 1, column=j, sticky="nsew")  # Creating and placing labels for past appointments

    for col in range(len(past_columns)):
        past_appointments_frame.grid_columnconfigure(col,
                                                     weight=1)  # Configuring column weights for past appointments frame

    upcoming_columns = ["Date", "Time", "Patient Name", "Reason", "Action"]
    for col in upcoming_columns:
        header = ctk.CTkLabel(upcoming_appointments_frame, text=col, font=("Arial", 14, "bold"), fg_color="#E0F7FA",
                              padx=5, pady=5)
        header.grid(row=0, column=upcoming_columns.index(col),
                    sticky="nsew")  # Creating and placing headers for upcoming appointments

    for i, appointment in enumerate(upcoming_appointments):
        appointment_id, date, time, patient_name, reason = appointment
        for j, value in enumerate(appointment[1:]):
            label = ctk.CTkLabel(upcoming_appointments_frame, text=value, font=("Arial", 12), fg_color="white", padx=5,
                                 pady=5)
            label.grid(row=i + 1, column=j, sticky="nsew")  # Creating and placing labels for upcoming appointments

        button_frame = ctk.CTkFrame(upcoming_appointments_frame,
                                    fg_color="white")  # Creating a frame for the action buttons
        button_frame.grid(row=i + 1, column=len(appointment[1:]), sticky="nsew")

        prescribe_button = ctk.CTkButton(button_frame, text="Generate Prescription",
                                         command=lambda appt_id=appointment_id,
                                                        pt_name=patient_name: create_prescription_form(appt_id,
                                                                                                       doctor_id,
                                                                                                       pt_name),
                                         fg_color="blue", text_color="white", font=("Arial", 12))
        record_button = ctk.CTkButton(button_frame, text="View Medical Record",
                                      command=lambda appt_id=appointment_id, pt_name=patient_name: view_medical_record(
                                          appt_id, pt_name), fg_color="green", text_color="white", font=("Arial", 12))

        prescribe_button.grid(row=0, column=0, sticky="nsew", padx=5,
                              pady=5)  # Creating and placing the generate prescription button
        record_button.grid(row=0, column=1, sticky="nsew", padx=5,
                           pady=5)  # Creating and placing the view medical record button

        button_frame.grid_columnconfigure(0, weight=1)  # Configuring column weights for button frame
        button_frame.grid_columnconfigure(1, weight=1)  # Configuring column weights for button frame

    for col in range(len(upcoming_columns)):
        upcoming_appointments_frame.grid_columnconfigure(col,
                                                         weight=1)  # Configuring column weights for upcoming appointments frame


# Get doctor_id from command-line arguments
doctor_id = sys.argv[1] if len(sys.argv) > 1 else None  # Getting doctor_id from command line arguments
if doctor_id:
    try:
        doctor_id = int(doctor_id)  # Converting doctor_id to integer
        doctor_fullname = get_doctor_fullname(doctor_id)  # Fetching the doctor's full name
    except ValueError as ve:
        print(f"ValueError: {ve}")
        doctor_fullname = "Unknown Doctor"
else:
    doctor_fullname = "Unknown Doctor"

# Create main window
ctk.set_appearance_mode("light")  # Setting appearance mode to light
ctk.set_default_color_theme("blue")  # Setting default color theme to blue

root = ctk.CTk()  # Creating the main tkinter window
root.title("Doctor Home Page")  # Setting window title
root.geometry("1000x700")  # Setting window dimensions
root.configure(fg_color="#AED6F1")  # Configuring the foreground color to light blue

# Image file path
image_path = "C:/Users/user/Documents/GitHub/SoftwareEng/Software_Project/Harvind/Images/"


# Function to load and resize images
def load_image(image_name, size):
    img = Image.open(image_path + image_name)  # Opening the image file
    img = img.resize(size, Image.Resampling.LANCZOS)  # Resizing the image
    return ctk.CTkImage(light_image=img, size=size)  # Returning the resized image as a CTkImage


# Load images with specified size
button_size = (40, 40)  # Setting the button size
profile_img = load_image("profile.png", button_size)  # Loading and resizing the profile image
logout_img = load_image("logout.png", button_size)  # Loading and resizing the logout image

# Left side menu
menu_frame = ctk.CTkFrame(root, fg_color="#E6E6FA")  # Creating a frame for the left side menu with light purple color
menu_frame.pack(side=ctk.LEFT, fill=ctk.Y, padx=10, pady=10)  # Packing the menu frame on the left side with padding


# Menu buttons with images and labels
def create_button(frame, image, text, command):
    button_frame = ctk.CTkFrame(frame, fg_color="#E6E6FA")  # Creating a frame for the button with light purple color
    button_frame.pack(fill=ctk.X, pady=5, padx=5)  # Packing the button frame with padding
    btn = ctk.CTkButton(button_frame, image=image, command=command, fg_color="white", hover_color="#AED6F1",
                        text="")  # Creating the button
    btn.pack(pady=0)  # Packing the button with no padding
    label = ctk.CTkLabel(button_frame, text=text, fg_color="#E6E6FA",
                         font=("Arial", 12, "bold"))  # Creating a label for the button
    label.pack(pady=5)  # Packing the label with padding
    return button_frame


create_button(menu_frame, profile_img, "PROFILE", profile_action)  # Creating the profile button
create_button(menu_frame, logout_img, "LOGOUT", logout_action)  # Creating the logout button

# Main content area
main_frame = ctk.CTkFrame(root, fg_color="#AED6F1")  # Creating the main frame with light blue color
main_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=20,
                pady=20)  # Packing the main frame on the right side with padding

# Welcome text
welcome_label = ctk.CTkLabel(main_frame, text=f"Welcome DR. {doctor_fullname}", font=("Arial", 24),
                             fg_color="#AED6F1")  # Creating a welcome label with doctor's name
welcome_label.pack(pady=20)  # Packing the welcome label with padding

# Past appointments section
past_appointments_label = ctk.CTkLabel(main_frame, text="PAST APPOINTMENTS", fg_color="#AED6F1",
                                       font=("Arial", 18))  # Creating a label for past appointments section
past_appointments_label.pack(fill=ctk.X, pady=(0, 10))  # Packing the label with padding

past_appointments_frame = ctk.CTkFrame(main_frame,
                                       fg_color="white")  # Creating a frame for past appointments with white color
past_appointments_frame.pack(fill=ctk.BOTH, expand=True)  # Packing the frame with both fill and expand options

# Upcoming appointments section
upcoming_appointments_label = ctk.CTkLabel(main_frame, text="UPCOMING APPOINTMENTS", fg_color="#AED6F1",
                                           font=("Arial", 18))  # Creating a label for upcoming appointments section
upcoming_appointments_label.pack(fill=ctk.X, pady=(10, 0))  # Packing the label with padding

upcoming_appointments_frame = ctk.CTkFrame(main_frame,
                                           fg_color="white")  # Creating a frame for upcoming appointments with white color
upcoming_appointments_frame.pack(fill=ctk.BOTH, expand=True)  # Packing the frame with both fill and expand options

# Fetch appointment data for the specific doctor
refresh_appointments()  # Calling the function to refresh appointments

root.mainloop()  # Running the main loop to display the window