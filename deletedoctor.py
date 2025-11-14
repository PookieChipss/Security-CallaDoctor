import customtkinter as ctk  # Import customtkinter for custom UI elements
import mysql.connector  # Import mysql.connector for database connectivity
import os  # Import os for operating system commands
import sys  # Import sys for handling command line arguments
from tkinter import messagebox  # Import messagebox from tkinter

# Get clinic ID and admin full name from command line arguments
if len(sys.argv) > 2:
    clinic_id = sys.argv[1]  # Get the clinic ID from command line argument
    admin_fullname = sys.argv[2]  # Get the admin full name from command line argument
else:
    clinic_id = "Unknown Clinic"  # Default clinic ID if not provided
    admin_fullname = "ADMIN"  # Default admin full name if not provided

# Function to delete a doctor
def delete_doctor(doctor_id, user_id):
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host='localhost',  # Database host
            user='root',  # Database username
            passwd='calladoctor1234',  # Database password
            database='calladoctor'  # Database name
        )
        cursor = connection.cursor()  # Create a cursor object to execute SQL queries
        # Delete doctor from doctors table
        cursor.execute('DELETE FROM doctors WHERE doctor_id = %s', (doctor_id,))
        # Delete user from users table
        cursor.execute('DELETE FROM users WHERE user_id = %s', (user_id,))
        connection.commit()  # Commit the transaction to the database
        messagebox.showinfo("Success", "Doctor deleted successfully!")  # Show success message
        load_doctors()  # Refresh the table after deletion
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")  # Show error message if any database error occurs
    finally:
        if connection.is_connected():
            cursor.close()  # Close the cursor
            connection.close()  # Close the database connection

# Function to load doctors from the database
def load_doctors():
    for widget in table_frame.winfo_children():  # Iterate over all child widgets in the table frame
        widget.destroy()  # Destroy each child widget to clear the table
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host='localhost',  # Database host
            user='root',  # Database username
            passwd='calladoctor1234',  # Database password
            database='calladoctor'  # Database name
        )
        cursor = connection.cursor()  # Create a cursor object to execute SQL queries
        # Query to get doctors associated with the clinic
        cursor.execute('''
            SELECT doctors.doctor_id, users.user_id, users.fullname, users.email, users.phone_number, doctors.identification_number, doctors.gender 
            FROM doctors 
            JOIN users ON doctors.user_id = users.user_id 
            WHERE doctors.clinic_id = %s
        ''', (clinic_id,))
        doctors = cursor.fetchall()  # Fetch all rows from the executed query
        create_table_header()  # Create the table header
        for index, doctor in enumerate(doctors):  # Iterate over each doctor
            create_table_row(index, doctor)  # Create a table row for each doctor
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")  # Show error message if any database error occurs
    finally:
        if connection.is_connected():
            cursor.close()  # Close the cursor
            connection.close()  # Close the database connection

# Function to confirm deletion of a doctor
def confirm_delete(doctor_id, user_id):
    response = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this doctor?")  # Show confirmation dialog
    if response:  # If user confirms
        delete_doctor(doctor_id, user_id)  # Delete the doctor

# Function to go back to the previous screen
def back_action():
    root.destroy()  # Destroy the current window
    os.system(f'python adminclinichome.py {clinic_id} {admin_fullname}')  # Run the adminclinichome script

# Function to create the table header
def create_table_header():
    headers = ["Doctor Name", "Email", "Tel", "IC", "Gender", "Delete Option"]  # List of headers for the table
    for col, header in enumerate(headers):  # Iterate over headers
        label = ctk.CTkLabel(table_frame, text=header, font=("Helvetica", 12, "bold"), pady=5, fg_color="#E0F7FA", text_color="black")  # Create a label for each header
        label.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)  # Place the label in the grid
        table_frame.grid_columnconfigure(col, weight=1)  # Make columns expandable

# Function to create a table row
def create_table_row(index, doctor):
    for col, value in enumerate(doctor[2:]):  # Iterate over doctor details (excluding IDs)
        label = ctk.CTkLabel(table_frame, text=value, font=("Helvetica", 12), pady=5, fg_color="#E0F7FA", text_color="black")  # Create a label for each detail
        label.grid(row=index + 1, column=col, sticky="nsew", padx=1, pady=1)  # Place the label in the grid
    # Create a delete button for each row
    delete_button = ctk.CTkButton(table_frame, text="Delete", command=lambda d=doctor[0], u=doctor[1]: confirm_delete(d, u), fg_color="red", text_color="white", font=("Helvetica", 12))
    delete_button.grid(row=index + 1, column=len(doctor[2:]), sticky="nsew", padx=1, pady=1)  # Place the delete button in the grid

# Create main window
root = ctk.CTk()
root.title("Delete Doctor")  # Set window title
root.geometry("1000x600")  # Set window size
root.configure(fg_color="lightblue")  # Set the window background color

# Title label
title_label = ctk.CTkLabel(root, text="Delete Doctor", font=("Helvetica", 24, "bold"), fg_color="lightblue", text_color="black")  # Create a title label
title_label.pack(pady=10)  # Pack the title label with padding

# Table frame
table_frame = ctk.CTkFrame(root, fg_color="lightblue")  # Create a frame to hold the table
table_frame.pack(pady=10, padx=100, fill=ctk.BOTH, expand=True)  # Pack the table frame with padding and expand it

# Create initial header for the table
create_table_header()

# Load doctors into the table
load_doctors()

# Back button
back_button = ctk.CTkButton(root, text="Back", command=back_action, font=("Helvetica", 12), text_color="Black", fg_color="#81D4FA")  # Create a back button
back_button.pack(side=ctk.BOTTOM, pady=20)  # Pack the back button at the bottom with padding

root.mainloop()  # Run the main loop for the application
