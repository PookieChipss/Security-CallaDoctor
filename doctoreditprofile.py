# Import necessary modules
import customtkinter as ctk  # Custom Tkinter for enhanced UI elements
from tkinter import messagebox  # Standard Tkinter message box for error and info dialogs
import mysql.connector  # MySQL connector to interact with the MySQL database
from mysql.connector import Error  # Error handling for MySQL operations
from PIL import Image, ImageTk  # Python Imaging Library for image processing
import doctorprofile  # Presumably a custom module for doctor profiles
import os  # Standard library for operating system interactions
import sys  # Standard library for interacting with the system parameters

# Function to fetch doctor details from the database
def fetch_doctor_details(doctor_id):
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='calladoctor1234',
            database='calladoctor'
        )
        cursor = connection.cursor()  # Create a cursor object
        # Execute SQL query to fetch doctor details
        cursor.execute('''
            SELECT d.fullname, u.username, d.identification_number, d.gender, u.address, u.date_of_birth, u.email, u.phone_number 
            FROM users u
            JOIN doctors d ON u.user_id = d.user_id
            WHERE d.doctor_id = %s
        ''', (doctor_id,))
        result = cursor.fetchone()  # Fetch a single row
        return result  # Return the result
    except Error as e:
        # Show error message if there's an issue with fetching details
        messagebox.showerror("Error", f"Error fetching doctor details: {e}")
    finally:
        # Ensure the database connection is closed
        if connection.is_connected():
            cursor.close()  # Close the cursor
            connection.close()  # Close the connection
    return None  # Return None if there's an error

# Function to update doctor details in the database
def update_doctor_details(doctor_id, address, email, phone_number):
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='calladoctor1234',
            database='calladoctor'
        )
        cursor = connection.cursor()  # Create a cursor object
        # Execute SQL query to update doctor details
        cursor.execute('''
            UPDATE users u
            JOIN doctors d ON u.user_id = d.user_id
            SET u.address = %s, u.email = %s, u.phone_number = %s
            WHERE d.doctor_id = %s
        ''', (address, email, phone_number, doctor_id))
        connection.commit()  # Commit the changes
    except Error as e:
        # Show error message if there's an issue with updating details
        messagebox.showerror("Error", f"Error updating doctor details: {e}")
    finally:
        # Ensure the database connection is closed
        if connection.is_connected():
            cursor.close()  # Close the cursor
            connection.close()  # Close the connection

# Function to load and resize an image
def load_image(image_path, size):
    try:
        img = Image.open(image_path)  # Open the image file
        img = img.resize(size, Image.Resampling.LANCZOS)  # Resize the image
        return ImageTk.PhotoImage(img)  # Convert image to PhotoImage format
    except Exception as e:
        # Show error message if there's an issue with loading the image
        messagebox.showerror("Error", f"Error loading image {image_path}: {e}")
        return None  # Return None if there's an error

# Function to navigate back to the home screen
def back_to_home(root, doctor_id):
    root.destroy()  # Close the current window
    doctorprofile.create_doctor_profile_window(doctor_id)  # Open the doctor profile window

# Function to validate the phone number input
def validate_phone_number(phone_number):
    if not phone_number.isdigit():  # Check if phone number contains only digits
        messagebox.showerror("Invalid Input", "Phone number must contain only digits.")  # Show error if not
        return False  # Return False if validation fails
    return True  # Return True if validation passes

# Function to create the doctor edit profile window
def create_doctor_edit_profile_window(doctor_id):
    global root
    ctk.set_appearance_mode("light")  # Set the appearance mode to light
    ctk.set_default_color_theme("blue")  # Set the default color theme to blue

    root = ctk.CTk()  # Create the main window
    root.title("Edit Profile (You can only edit the blue field)")  # Set the window title
    root.geometry("550x550")  # Set the window size

    # Create the main content area frame
    main_frame = ctk.CTkFrame(root, fg_color="lightblue")
    main_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=20, pady=20)

    # Create the profile section frame
    profile_frame = ctk.CTkFrame(main_frame, fg_color="lightblue", corner_radius=10)
    profile_frame.pack(expand=True, pady=10, ipadx=20, ipady=20)

    # Create the profile label
    profile_label = ctk.CTkLabel(profile_frame, text="EDIT PROFILE (You can only edit the white field)", font=("Arial", 16, "bold"))
    profile_label.grid(row=0, columnspan=2, pady=20)

    # Labels for the profile fields
    labels = ["Fullname:", "Username:", "IC:", "Gender:", "Address:", "Date of Birth:", "Email:", "Tel:"]
    doctor_details = fetch_doctor_details(doctor_id)  # Fetch the doctor details
    entries = []  # List to store the entry widgets

    if doctor_details:
        for i, label_text in enumerate(labels):
            # Create a label for each field
            label = ctk.CTkLabel(profile_frame, text=label_text, font=("Arial", 12))
            label.grid(row=i + 1, column=0, sticky="e", padx=5, pady=5)
            # Set the entry field color based on whether it is editable
            entry_fg_color = "white" if label_text in ["Address:", "Email:", "Tel:"] else "lightblue"
            entry = ctk.CTkEntry(profile_frame, font=("Arial", 12), fg_color=entry_fg_color)
            entry.grid(row=i + 1, column=1, sticky="w", padx=5, pady=5)
            entry.insert(0, doctor_details[i])  # Insert the existing detail into the entry field
            if label_text not in ["Address:", "Email:", "Tel:"]:
                entry.configure(state='readonly')  # Make the field read-only if it's not editable
            entries.append(entry)  # Add the entry to the list

        # Function to save changes to the database
        def save_changes():
            address = entries[4].get()  # Get the address from the entry field
            email = entries[6].get()  # Get the email from the entry field
            phone_number = entries[7].get()  # Get the phone number from the entry field
            if not validate_phone_number(phone_number):  # Validate the phone number
                return
            update_doctor_details(doctor_id, address, email, phone_number)  # Update the details in the database
            messagebox.showinfo("Success", "Profile updated successfully")  # Show success message
            root.destroy()  # Close the current window
            doctorprofile.create_doctor_profile_window(doctor_id)  # Open the doctor profile window

        # Function to confirm changes before saving
        def confirm_changes():
            response = messagebox.askyesno("Confirm Changes", "Are you sure you want to make the changes?")  # Ask for confirmation
            if response:
                save_changes()  # Save changes if confirmed

        # Create a confirm button
        confirm_button = ctk.CTkButton(profile_frame, text="Confirm", font=("Arial", 12), command=confirm_changes)
        confirm_button.grid(row=len(labels) + 1, columnspan=2, pady=10)

        # Create a back button
        back_button = ctk.CTkButton(profile_frame, text="Back", font=("Arial", 12), command=lambda: back_to_home(root, doctor_id))
        back_button.grid(row=len(labels) + 2, columnspan=2, pady=10)
    else:
        messagebox.showerror("Error", "User details not found!")  # Show error if user details are not found

    root.mainloop()  # Start Tkinter main loop

# Entry point of the script
if __name__ == "__main__":
    if len(sys.argv) > 1:
        doctor_id = int(sys.argv[1])  # Get doctor ID from command line arguments
    else:
        doctor_id = 15  # Default doctor ID for testing

    create_doctor_edit_profile_window(doctor_id)  # Create the edit profile window with the doctor ID