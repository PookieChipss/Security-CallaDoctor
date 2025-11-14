import customtkinter as ctk  # Import customtkinter for creating custom UI elements
from tkcalendar import DateEntry  # Import DateEntry from tkcalendar for date selection
import mysql.connector  # Import mysql.connector for database connectivity
import sys  # Import sys for handling command line arguments
from tkinter import messagebox, ttk  # Import messagebox and ttk from tkinter

# Ensure command line arguments are properly passed
if len(sys.argv) > 2:
    clinic_id = sys.argv[1]
    admin_fullname = sys.argv[2]
else:
    clinic_id = "Unknown Clinic"
    admin_fullname = "ADMIN"

print(f"Clinic ID: {clinic_id}, Admin Fullname: {admin_fullname}")

# Function to fetch and display doctors based on selected date and time
def fetch_doctors():
    selected_date = date_entry.get_date()  # Get selected date
    selected_hour = hour_combobox.get()  # Get selected hour
    selected_minute = minute_combobox.get()  # Get selected minute

    selected_time = f"{selected_hour}:{selected_minute}:00"  # Format selected time
    formatted_date = selected_date.strftime("%Y-%m-%d")  # Convert the selected date to YYYY-MM-DD format

    print(f"Selected Date: {formatted_date}, Selected Time: {selected_time}, Clinic ID: {clinic_id}")

    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='calladoctor1234',
            database='calladoctor'
        )
        cursor = connection.cursor()

        # Clear treeview before fetching data
        for item in tree.get_children():
            tree.delete(item)

        # Query to get available doctors
        query = """
        SELECT d.fullname
        FROM doctors d
        LEFT JOIN appointments a ON d.doctor_id = a.doctor_id 
            AND a.appointment_date = %s 
            AND a.appointment_time = %s 
            AND a.appointment_request_status = 'accepted'
        WHERE d.clinic_id = %s 
          AND d.is_available = 1 
          AND (a.doctor_id IS NULL OR a.appointment_request_status != 'accepted')
        """
        print(f"Executing query with params: {formatted_date}, {selected_time}, {clinic_id}")
        cursor.execute(query, (formatted_date, selected_time, clinic_id))
        doctors = cursor.fetchall()

        # Insert fetched doctors into the treeview
        for index, doctor in enumerate(doctors, start=1):
            tree.insert("", "end", values=(index, doctor[0]))

        if not doctors:
            # When no doctors are available, list all available doctors regardless of appointment time
            query = """
            SELECT fullname 
            FROM doctors 
            WHERE clinic_id = %s 
              AND is_available = 1
            """
            cursor.execute(query, (clinic_id,))
            doctors = cursor.fetchall()

            for index, doctor in enumerate(doctors, start=1):
                tree.insert("", "end", values=(index, doctor[0]))

            if not doctors:
                messagebox.showinfo("No Doctors Available", "No available doctors found for the selected date and time.")

        connection.close()

    except mysql.connector.Error as error:
        print(f"Database Error: {error}")
        messagebox.showerror("Database Error", str(error))

# Function to clear the table
def clear_table():
    for item in tree.get_children():
        tree.delete(item)

# Function to close the current window
def close_window():
    root.destroy()

# Create main application window
ctk.set_appearance_mode("light")  # Set appearance mode
ctk.set_default_color_theme("blue")  # Set color theme

root = ctk.CTk()
root.title("Appointment Schedule Page")
root.geometry("500x600")
root.configure(fg_color="#E0F7FA")

# Date selection
date_label = ctk.CTkLabel(root, text="Select Date:", fg_color="#E0F7FA")
date_label.pack(pady=5)

date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, font=("Arial", 12))
date_entry.pack(pady=5)

# Time selection
time_label = ctk.CTkLabel(root, text="Select Time:", fg_color="#E0F7FA", font=("Arial", 12))
time_label.pack(pady=5)

time_frame = ctk.CTkFrame(root, fg_color="#E0F7FA")
time_frame.pack(pady=5)

# Using Combobox for better time selection
hour_combobox = ttk.Combobox(time_frame, values=[f"{i:02d}" for i in range(24)], width=3, font=("Arial", 12))
hour_combobox.set("09")  # Default selection
hour_combobox.pack(side=ctk.LEFT, padx=5)

minute_combobox = ttk.Combobox(time_frame, values=[f"{i:02d}" for i in range(0, 60, 15)], width=3, font=("Arial", 12))
minute_combobox.set("00")  # Default selection
minute_combobox.pack(side=ctk.LEFT, padx=5)

# Buttons frame
buttons_frame = ctk.CTkFrame(root, fg_color="#E0F7FA")
buttons_frame.pack(pady=10)

# Search button
search_button = ctk.CTkButton(buttons_frame, text="Search", command=fetch_doctors)
search_button.pack(side=ctk.LEFT, padx=10)

# Back button
back_button = ctk.CTkButton(buttons_frame, text="Back", command=close_window)
back_button.pack(side=ctk.LEFT, padx=10)

# Table title
table_title = ctk.CTkLabel(root, text="Available Doctors", font=("Arial", 14, "bold"), fg_color="#E0F7FA")
table_title.pack(pady=5)

# Treeview to display doctors
tree = ttk.Treeview(root, columns=("no", "doctor_name"), show='headings', height=10)
tree.heading("no", text="No.")
tree.heading("doctor_name", text="Doctor")
tree.column("no", anchor=ctk.CENTER, width=50, minwidth=50)
tree.column("doctor_name", anchor=ctk.CENTER, width=200, minwidth=200)

# Add color to the columns
style = ttk.Style()
style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
style.configure("Treeview", rowheight=25)
style.configure("Treeview", background="white", fieldbackground="white")
style.map("Treeview", background=[('selected', 'lightgreen')])

tree.pack(pady=10, fill=ctk.X, expand=False)

# Run the application
root.mainloop()