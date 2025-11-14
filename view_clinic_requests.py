import customtkinter as ctk  # Import customtkinter library as ctk
from tkinter import messagebox, ttk, Toplevel, Label  # Import messagebox, ttk, Toplevel, and Label from tkinter
from PIL import Image, ImageTk  # Import Image and ImageTk modules from PIL
import mysql.connector  # Import mysql.connector library for MySQL database connection
import os  # Import os module for operating system functions
import sys  # Import sys module for system-specific parameters and functions
import io  # Import io module for dealing with I/O operations

# Get admin's full name from command line argument
if len(sys.argv) > 1:
    admin_fullname = sys.argv[1]  # Retrieve admin's full name from command line argument
else:
    admin_fullname = "ADMIN"  # Default value for admin's full name if not provided

# Function to fetch pending clinics
def fetch_pending_clinics():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='calladoctor1234',
            database='calladoctor'
        )  # Establish connection to MySQL database
        cursor = connection.cursor()  # Create cursor object
        query = "SELECT clinic_id, clinic_name, address FROM clinics WHERE is_approved = 0"  # SQL query to fetch pending clinics
        cursor.execute(query)  # Execute SQL query
        result = cursor.fetchall()  # Fetch all rows
        cursor.close()  # Close cursor
        connection.close()  # Close connection
        return result  # Return fetched rows
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", f"Failed to fetch data: {error}")  # Show error message if database error occurs
        return []  # Return empty list on error

# Function to approve clinic
def approve_clinic():
    selected_item = tree.focus()  # Get currently selected item in the Treeview
    if not selected_item:
        messagebox.showwarning("No Selection", "Please choose a clinic to approve.")  # Show warning if no clinic is selected
        return

    clinic_id = tree.item(selected_item)['values'][0]  # Get clinic_id of the selected clinic
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='calladoctor1234',
            database='calladoctor'
        )  # Establish connection to MySQL database
        cursor = connection.cursor()  # Create cursor object
        query = "UPDATE clinics SET is_approved = 1 WHERE clinic_id = %s"  # SQL query to approve clinic
        cursor.execute(query, (clinic_id,))  # Execute SQL query with parameter
        connection.commit()  # Commit changes
        cursor.close()  # Close cursor
        connection.close()  # Close connection
        messagebox.showinfo("Success", "Clinic approved successfully!")  # Show success message
        refresh_table()  # Refresh the table of pending clinics
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", f"Failed to approve clinic: {error}")  # Show error message on database error

# Function to reject clinic
def reject_clinic():
    selected_item = tree.focus()  # Get currently selected item in the Treeview
    if not selected_item:
        messagebox.showwarning("No Selection", "Please choose a clinic to reject.")  # Show warning if no clinic is selected
        return

    clinic_id = tree.item(selected_item)['values'][0]  # Get clinic_id of the selected clinic
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='calladoctor1234',
            database='calladoctor'
        )  # Establish connection to MySQL database
        cursor = connection.cursor()  # Create cursor object
        query = "DELETE FROM clinics WHERE clinic_id = %s"  # SQL query to delete clinic
        cursor.execute(query, (clinic_id,))  # Execute SQL query with parameter
        connection.commit()  # Commit changes
        cursor.close()  # Close cursor
        connection.close()  # Close connection
        messagebox.showinfo("Success", "Clinic rejected successfully!")  # Show success message
        refresh_table()  # Refresh the table of pending clinics
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", f"Failed to reject clinic: {error}")  # Show error message on database error

# Function to refresh the table
def refresh_table():
    for item in tree.get_children():
        tree.delete(item)  # Delete all items from the Treeview

    pending_clinics = fetch_pending_clinics()  # Fetch pending clinics
    for clinic in pending_clinics:
        tree.insert("", "end", values=(clinic[0], clinic[1], clinic[2]))  # Insert clinic data into Treeview

# Function to the view clinic license
def view_license():
    selected_item = tree.focus()  # Get currently selected item in Treeview
    if not selected_item:
        messagebox.showwarning("No Selection", "Please choose a clinic to view the license.")  # Show warning if no clinic is selected
        return

    clinic_id = tree.item(selected_item)['values'][0]  # Get clinic_id of the selected clinic
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='calladoctor1234',
            database='calladoctor'
        )  # Establish connection to MySQL database
        cursor = connection.cursor()  # Create cursor object
        query = "SELECT clinic_license FROM clinics WHERE clinic_id = %s"  # SQL query to fetch clinic license
        cursor.execute(query, (clinic_id,))  # Execute SQL query with parameter
        result = cursor.fetchone()  # Fetch one row
        cursor.close()  # Close cursor
        connection.close()  # Close connection

        if result and result[0]:
            image_data = result[0]  # Get image data from the result
            image = Image.open(io.BytesIO(image_data))  # Open image from byte data
            image = image.resize((400, 400), Image.LANCZOS)  # Resize image
            photo = ImageTk.PhotoImage(image)  # Create PhotoImage from image

            top = Toplevel(root)  # Create Toplevel window
            top.title("Clinic License")  # Set window title
            label = Label(top, image=photo)  # Create label with image
            label.image = photo  # Attach image to label
            label.pack()  # Pack label to window
        else:
            messagebox.showinfo("No License", "This clinic does not have a license image.")  # Show info message if no license
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", f"Failed to fetch license: {error}")  # Show error message on database error

# Function for back button
def back_to_home():
    root.destroy()  # Destroy the main window
    os.system(f'python "C:/Users/user/Documents/GitHub/SoftwareEng/Software_Project/Harvind/adminhome.py" "{admin_fullname}"')  # Navigate back to admin home page

# Create main window
ctk.set_appearance_mode("light")  # Set appearance mode of customtkinter
ctk.set_default_color_theme("blue")  # Set default color theme of customtkinter

root = ctk.CTk()  # Create customtkinter window
root.title("Pending Clinic Registrations")  # Set window title
root.geometry("800x600")  # Set window size
root.configure(bg="white")  # Set background color

# Style for Treeview
style = ttk.Style()  # Create ttk style object
style.configure("Custom.Treeview", font=("Arial", 12), rowheight=25)  # Configure style for Treeview
style.configure("Custom.Treeview.Heading", font=("Arial", 12, "bold"), anchor="center")  # Configure style for Treeview headings

# Table for pending clinics
columns = ("Clinic ID", "Clinic Name", "Clinic Address")  # Define columns for Treeview
tree = ttk.Treeview(root, columns=columns, show="headings", style="Custom.Treeview")  # Create Treeview widget
tree.heading("Clinic ID", text="Clinic ID", anchor="center")  # Set heading for Clinic ID column
tree.heading("Clinic Name", text="Clinic Name", anchor="center")  # Set heading for Clinic Name column
tree.heading("Clinic Address", text="Clinic Address", anchor="center")  # Set heading for Clinic Address column
tree.column("Clinic ID", anchor="center")  # Set anchor for Clinic ID column
tree.column("Clinic Name", anchor="center")  # Set anchor for Clinic Name column
tree.column("Clinic Address", anchor="center")  # Set anchor for Clinic Address column

refresh_table()  # Refresh the table of pending clinics

tree.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)  # Pack Treeview to window

# Approve button
approve_btn = ctk.CTkButton(root, text="Approve", command=approve_clinic, font=("Arial", 12))  # Create custom button for approving clinics
approve_btn.pack(side=ctk.LEFT, padx=20, pady=20)  # Pack button to window

# Reject button
reject_btn = ctk.CTkButton(root, text="Reject", command=reject_clinic, font=("Arial", 12))  # Create custom button for rejecting clinics
reject_btn.pack(side=ctk.LEFT, padx=20, pady=20)  # Pack button to window

# View License button
view_license_btn = ctk.CTkButton(root, text="View License", command=view_license, font=("Arial", 12))  # Create custom button for viewing clinic license
view_license_btn.pack(side=ctk.LEFT, padx=20, pady=20)  # Pack button to window

# Back button
back_btn = ctk.CTkButton(root, text="Back", command=back_to_home, font=("Arial", 12))  # Create custom button for going back to admin home
back_btn.pack(side=ctk.RIGHT, padx=20, pady=20)  # Pack button to window

root.mainloop()  # Run main loop