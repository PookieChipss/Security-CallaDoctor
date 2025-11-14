import customtkinter as ctk  # Importing custom tkinter library as ctk
from tkinter import messagebox  # Importing messagebox from tkinter for showing dialogs
import mysql.connector  # Importing MySQL Connector Python module
from mysql.connector import Error  # Importing Error class from mysql.connector
from PIL import Image, ImageTk  # Importing necessary classes from PIL library
import patientprofile  # Importing patientprofile module
import os  # Importing os module for interacting with the operating system
import sys  # Importing sys module for accessing command-line arguments

# Function to fetch patient details from the database
def fetch_patient_details(patient_id):
    try:
        # Establishing connection to MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='calladoctor1234',
            database='calladoctor'
        )
        cursor = connection.cursor()  # Creating a cursor object

        # Query to fetch patient details
        cursor.execute('''
            SELECT u.fullname, u.username, p.identification_number, p.gender, u.address, u.date_of_birth, u.email, u.phone_number 
            FROM users u
            JOIN patients p ON u.user_id = p.user_id
            WHERE p.patient_id = %s
        ''', (patient_id,))
        result = cursor.fetchone()  # Fetching the result
        return result  # Returning the fetched result
    except Error as e:
        messagebox.showerror("Error", f"Error fetching patient details: {e}")  # Showing error message in case of exception
    finally:
        if connection.is_connected():
            cursor.close()  # Closing the cursor
            connection.close()  # Closing the connection
    return None  # Returning None if there was an error

# Function to update patient details in the database
def update_patient_details(patient_id, address, email, phone_number):
    try:
        # Establishing connection to MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='calladoctor1234',
            database='calladoctor'
        )
        cursor = connection.cursor()  # Creating a cursor object

        # Query to update patient details
        cursor.execute('''
            UPDATE users u
            JOIN patients p ON u.user_id = p.user_id
            SET u.address = %s, u.email = %s, u.phone_number = %s
            WHERE p.patient_id = %s
        ''', (address, email, phone_number, patient_id))
        connection.commit()  # Committing the transaction
    except Error as e:
        messagebox.showerror("Error", f"Error updating patient details: {e}")  # Showing error message in case of exception
    finally:
        if connection.is_connected():
            cursor.close()  # Closing the cursor
            connection.close()  # Closing the connection

# Function to load and resize an image
def load_image(image_path, size):
    try:
        img = Image.open(image_path)  # Opening the image
        img = img.resize(size, Image.ANTIALIAS)  # Resizing the image
        return ImageTk.PhotoImage(img)  # Returning the image as a PhotoImage
    except Exception as e:
        messagebox.showerror("Error", f"Error loading image {image_path}: {e}")  # Showing error message in case of exception
        return None

# Function to go back to the patient profile page
def back_to_home(root, patient_id, patient_fullname):
    root.destroy()  # Destroying the current window
    patientprofile.create_patient_profile_window(patient_id, patient_fullname)  # Creating patient profile window

# Function to validate phone number
def validate_phone_number(phone_number):
    if not phone_number.isdigit():  # Checking if phone number contains only digits
        messagebox.showerror("Invalid Input", "Phone number must contain only digits.")  # Showing error message
        return False  # Returning False if validation fails
    return True  # Returning True if validation passes

# Function to create the edit profile window for the patient
def create_patient_edit_profile_window(patient_id, patient_fullname):
    global root  # Using global variable for the root window

    ctk.set_appearance_mode("light")  # Setting appearance mode to light
    ctk.set_default_color_theme("blue")  # Setting default color theme to blue

    root = ctk.CTk()  # Creating the main tkinter window
    root.title("Edit Profile (You can only edit the blue field)")  # Setting window title
    root.geometry("550x550")  # Setting window dimensions

    # Main content area
    main_frame = ctk.CTkFrame(root, fg_color="lightblue")  # Creating the main frame
    main_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=20, pady=20)  # Packing the main frame

    # Profile section
    profile_frame = ctk.CTkFrame(main_frame, fg_color="lightblue", corner_radius=10)  # Creating the profile frame
    profile_frame.pack(expand=True, pady=10, ipadx=20, ipady=20)  # Packing the profile frame

    # Label for edit profile section
    profile_label = ctk.CTkLabel(profile_frame, text="EDIT PROFILE (You can only edit the white field)", font=("Arial", 16, "bold"))
    profile_label.grid(row=0, columnspan=2, pady=20)  # Grid layout for label

    # Labels for patient details
    labels = ["Fullname:", "Username:", "IC:", "Gender:", "Address:", "Date of Birth:", "Email:", "Tel:"]
    patient_details = fetch_patient_details(patient_id)  # Fetching patient details
    entries = []  # List to store entry widgets

    if patient_details:
        for i, label_text in enumerate(labels):
            label = ctk.CTkLabel(profile_frame, text=label_text, font=("Arial", 12))
            label.grid(row=i + 1, column=0, sticky="e", padx=5, pady=5)

            # Setting foreground color for editable fields
            entry_fg_color = "white" if label_text in ["Address:", "Email:", "Tel:"] else "lightblue"
            entry = ctk.CTkEntry(profile_frame, font=("Arial", 12), fg_color=entry_fg_color)
            entry.grid(row=i + 1, column=1, sticky="w", padx=5, pady=5)
            entry.insert(0, patient_details[i])  # Inserting patient details into entry
            if label_text not in ["Address:", "Email:", "Tel:"]:
                entry.configure(state='readonly')  # Making non-editable fields readonly
            entries.append(entry)  # Appending entry to entries list

        # Function to save changes made to profile
        def save_changes():
            address = entries[4].get()
            email = entries[6].get()
            phone_number = entries[7].get()
            if not validate_phone_number(phone_number):  # Validating phone number
                return
            update_patient_details(patient_id, address, email, phone_number)  # Updating patient details
            messagebox.showinfo("Success", "Profile updated successfully")  # Showing success message
            root.destroy()  # Destroying current window
            patientprofile.create_patient_profile_window(patient_id, patient_fullname)  # Creating patient profile window

        # Function to confirm changes made to profile
        def confirm_changes():
            response = messagebox.askyesno("Confirm Changes", "Are you sure you want to make the changes?")  # Confirm dialog
            if response:
                save_changes()  # Saving changes

        # Confirm button
        confirm_button = ctk.CTkButton(profile_frame, text="Confirm", font=("Arial", 12), command=confirm_changes)
        confirm_button.grid(row=len(labels) + 1, columnspan=2, pady=10)

        # Back button
        back_button = ctk.CTkButton(profile_frame, text="Back", font=("Arial", 12), command=lambda: back_to_home(root, patient_id, patient_fullname))
        back_button.grid(row=len(labels) + 2, columnspan=2, pady=10)
    else:
        messagebox.showerror("Error", "User details not found!")  # Showing error message if user details not found

    root.mainloop()  # Running main loop

if __name__ == "__main__":
    # Checking command-line arguments
    if len(sys.argv) > 2:
        patient_id = int(sys.argv[1])  # Extracting patient_id from command line argument
        patient_fullname = sys.argv[2]  # Extracting patient_fullname from command line argument
    else:
        patient_id = 1  # Default patient_id for testing
        patient_fullname = "PATIENT"

    create_patient_edit_profile_window(patient_id, patient_fullname)  # Creating patient edit profile window