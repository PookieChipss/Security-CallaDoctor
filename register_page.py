import customtkinter as ctk  # Import customtkinter module (assuming it's a custom tkinter library)
from PIL import Image, ImageDraw, ImageTk  # Import necessary classes from Pillow
import mysql.connector  # Import mysql.connector for MySQL database connection

# Create rounded image function
def create_rounded_image(image_path, size, corner_radius):
    # Open and resize the image, then convert it to RGBA mode
    image = Image.open(image_path).resize(size, Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", image.size, 0)  # Create a mask
    draw = ImageDraw.Draw(mask)  # Create a draw object for the mask
    draw.rounded_rectangle((0, 0, size[0], size[1]), corner_radius, fill=255)  # Draw a rounded rectangle on the mask
    rounded_image = Image.new("RGBA", image.size)  # Create a new RGBA image
    rounded_image.paste(image, (0, 0), mask)  # Paste the image onto the rounded image using the mask
    return rounded_image  # Return the rounded image

# Create rounded button image function
def create_rounded_button_image(image_path, size, corner_radius):
    return create_rounded_image(image_path, size, corner_radius)  # Use create_rounded_image to create a rounded button image

# Button click events
def patient_button_clicked():
    register_root.destroy()  # Destroy the register window
    import patientregister  # Import patientregister module
    patientregister.create_patient_register_window()  # Call create_patient_register_window from patientregister

def clinic_button_clicked():
    register_root.destroy()  # Destroy the register window
    import clinicregister  # Import clinicregister module
    clinicregister.create_clinic_register_window()  # Call create_clinic_register_window from clinicregister

def open_login_page():
    register_root.destroy()  # Destroy the register window
    import main_page  # Import main_page module
    main_page.create_login_window()  # Call create_login_window from main_page

# Create register window function
def create_register_window():
    global register_root  # Declare register_root as global
    ctk.set_appearance_mode("light")  # Set appearance mode of customtkinter to light
    ctk.set_default_color_theme("blue")  # Set the default color theme of customtkinter to blue

    register_root = ctk.CTk()  # Create a custom tkinter window
    register_root.title("Register")  # Set the title of the window
    width = 600  # Set the width of the window
    height = 500  # Set the height of the window
    register_root.geometry(f"{width}x{height}")  # Set the size of the window

    top_frame = ctk.CTkFrame(register_root, fg_color="#ADD8E6", width=width, height=height)  # Create a frame with specific background color and size
    top_frame.pack(fill="both", expand=True)  # Pack the frame to fill both directions and expand to fill

    # Path to the logo image
    image_path = "C://Users//user//Documents//GitHub//SoftwareEng//Software_Project//Harvind//Images//SoftwareLogo.png"
    # Create a rounded logo image
    logo_image = create_rounded_image(image_path, (100, 100), 20)
    logo_photo = ctk.CTkImage(light_image=logo_image, size=(100, 100))  # Create a custom tkinter image
    logo_label = ctk.CTkLabel(top_frame, image=logo_photo, fg_color="#ADD8E6", text="")  # Create a label with an image
    logo_label.place(relx=0.99, rely=0.01, anchor="ne")  # Place the logo label in the top-right corner

    welcome_label = ctk.CTkLabel(top_frame, text="Welcome to Registration", font=("Times New Roman", 28), fg_color="#ADD8E6", text_color="#13126C")
    welcome_label.place(relx=0.5, rely=0.1, anchor="center")  # Place the welcome label in the center

    button_size = (120, 120)  # Set the size of the buttons
    corner_radius = 15  # Set the corner radius for rounded buttons

    # Path to the patient button image
    patient_image_path = "C://Users//user//Documents//GitHub//SoftwareEng//Software_Project//Harvind//Images//Patient.png"
    # Create a rounded patient button image
    patient_image = create_rounded_button_image(patient_image_path, button_size, corner_radius)
    patient_photo = ctk.CTkImage(light_image=patient_image, size=button_size)  # Create a custom tkinter image

    # Path to the clinic button image
    clinic_image_path = "C://Users//user//Documents//GitHub//SoftwareEng//Software_Project//Harvind//Images//Clinic.png"
    # Create a rounded clinic button image
    clinic_image = create_rounded_button_image(clinic_image_path, button_size, corner_radius)
    clinic_photo = ctk.CTkImage(light_image=clinic_image, size=button_size)  # Create a custom tkinter image

    # Create patient button
    patient_button = ctk.CTkButton(top_frame, image=patient_photo, command=patient_button_clicked, fg_color="#ADD8E6", hover_color="#5A9BD4", text="")
    patient_button.place(relx=0.35, rely=0.45, anchor="center")  # Place the patient button

    # Create clinic button
    clinic_button = ctk.CTkButton(top_frame, image=clinic_photo, command=clinic_button_clicked, fg_color="#ADD8E6", hover_color="#5A9BD4", text="")
    clinic_button.place(relx=0.65, rely=0.45, anchor="center")  # Place the clinic button

    patient_label = ctk.CTkLabel(top_frame, text="Patient", font=("Arial", 16), fg_color="#ADD8E6", text_color="black")
    patient_label.place(relx=0.35, rely=0.60, anchor="center")  # Place the patient label

    clinic_label = ctk.CTkLabel(top_frame, text="Clinic", font=("Arial", 16), fg_color="#ADD8E6", text_color="black")
    clinic_label.place(relx=0.65, rely=0.60, anchor="center")  # Place the clinic label

    login_frame = ctk.CTkFrame(top_frame, fg_color="#ADD8E6")  # Create a frame for the login section
    login_frame.place(relx=0.99, rely=0.99, anchor="se")  # Place the login frame in the bottom-right corner

    # Create login label
    login_label_text = ctk.CTkLabel(login_frame, text="Already have an account, ", font=("Arial", 16), fg_color="#ADD8E6", text_color="black")
    login_label_text.pack(side="left")  # Pack the login label to the left

    # Create click here label for login
    click_here_login_label = ctk.CTkLabel(login_frame, text="click here", font=("Arial", 16), fg_color="#ADD8E6", text_color="#0000EE", cursor="hand2")
    click_here_login_label.pack(side="left")  # Pack the click here label to the left
    click_here_login_label.bind("<Button-1>", lambda event: open_login_page())  # Bind click event to open login page

    register_root.mainloop()  # Run the main event loop

if __name__ == "__main__":
    create_register_window()  # Call function to create register window