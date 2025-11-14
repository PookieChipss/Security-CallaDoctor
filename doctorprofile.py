import sys  # Importing the sys module for system-specific parameters and functions
import customtkinter as ctk  # Importing customtkinter as ctk for custom tkinter widgets
from tkinter import messagebox  # Importing messagebox from tkinter for displaying dialogs
import mysql.connector  # Importing mysql.connector for MySQL database connectivity
from mysql.connector import Error  # Importing Error from mysql.connector for handling errors
import os  # Importing os module for interacting with the operating system


# Function to fetch doctor details based on doctor_id
def fetch_doctor_details(doctor_id):
    try:
        # Establishing a connection to the database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='calladoctor1234',
            database='calladoctor'
        )
        cursor = connection.cursor()  # Creating a cursor object to execute SQL queries

        # Executing the SQL query to fetch doctor details
        cursor.execute('''
            SELECT d.fullname, u.username, d.identification_number, d.gender, u.address, u.date_of_birth, u.email, u.phone_number 
            FROM users u
            JOIN doctors d ON u.user_id = d.user_id
            WHERE d.doctor_id = %s
        ''', (doctor_id,))

        # Fetching the first row from the result set
        result = cursor.fetchone()

        return result  # Returning the fetched result
    except Error as e:
        messagebox.showerror("Error", f"Error fetching doctor details: {e}")  # Showing error message box
    finally:
        # Closing cursor and database connection in the finally block
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

    return None  # Returning None if an error occurred


# Function to navigate back to the doctor's home page
def back_to_home(doctor_id):
    root.destroy()  # Destroying the current window
    # Navigating back to the doctor's home page using os.system
    os.system(
        f'python "C:/Users/user/Documents/GitHub/SoftwareEng/Software_Project/Harvind/doctorhome.py" {doctor_id}')


# Function to create doctor profile window
def create_doctor_profile_window(doctor_id):
    global root  # Declaring root as a global variable

    # Setting appearance mode and default color theme for customtkinter
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()  # Creating the main tkinter window
    root.title("Doctor Profile")  # Setting title of the window
    root.geometry("550x550")  # Setting the window size

    # Main content area frame
    main_frame = ctk.CTkFrame(root, fg_color="lightblue")  # Creating a frame for main content
    main_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=20, pady=20)  # Packing the main frame

    # Fetch doctor details
    doctor_details = fetch_doctor_details(doctor_id)

    # Checking if doctor details are fetched successfully
    if not doctor_details:
        messagebox.showerror("Error", "Doctor details not found!")  # Showing error message box
        root.destroy()  # Destroying the window
        return

    # Profile section frame
    profile_frame = ctk.CTkFrame(main_frame, fg_color="lightblue", corner_radius=10)  # Creating a frame for profile
    profile_frame.pack(expand=True, pady=10, ipadx=20, ipady=20)  # Packing the profile frame

    # Label for the profile section
    profile_label = ctk.CTkLabel(profile_frame, text="DOCTOR PROFILE", font=("Arial", 16, "bold"))
    profile_label.grid(row=0, columnspan=2, pady=20)  # Placing the profile label

    # Labels and corresponding entry widgets for doctor details
    labels = ["Fullname:", "Username:", "IC:", "Gender:", "Address:", "Date of Birth:", "Email:", "Tel:"]

    for i, label_text in enumerate(labels):
        label = ctk.CTkLabel(profile_frame, text=label_text, font=("Arial", 12))
        label.grid(row=i + 1, column=0, sticky="e", padx=5, pady=5)
        entry = ctk.CTkEntry(profile_frame, font=("Arial", 12))
        entry.grid(row=i + 1, column=1, sticky="w", padx=5, pady=5)
        entry.insert(0, doctor_details[i])
        entry.configure(state='readonly')

    edit_button = ctk.CTkButton(profile_frame, text="Edit Profile", font=("Arial", 12),
                                command=lambda: edit_profile_action(root, doctor_id))
    edit_button.grid(row=len(labels) + 1, columnspan=2, pady=10)

    back_button = ctk.CTkButton(profile_frame, text="Back", font=("Arial", 12),
                                command=lambda: back_to_home(doctor_id))
    back_button.grid(row=len(labels) + 2, columnspan=2, pady=10)

    root.mainloop()  # Starting the main loop for the tkinter window


# Function to handle editing of doctor profile
def edit_profile_action(root, doctor_id):
    root.destroy()  # Destroying the current window
    import doctoreditprofile  # Importing the module for editing doctor profile
    doctoreditprofile.create_doctor_edit_profile_window(doctor_id)  # Calling the function to create edit profile window


# Main entry point of the program
if __name__ == "__main__":
    if len(sys.argv) > 1:
        doctor_id = int(sys.argv[1])  # Fetching doctor_id from command line argument
    else:
        doctor_id = 1  # Example doctor_id for testing

    create_doctor_profile_window(doctor_id)  # Calling the function to create doctor profile window