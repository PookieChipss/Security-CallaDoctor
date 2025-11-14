import mysql.connector
from mysql.connector import Error

def create_connection(host='localhost', username='root', password='calladoctor1234', database='calladoctor'):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=username,
            passwd=password,
            database=database
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

# Replace with your own database connection details
connection = create_connection("localhost", "root", "calladoctor1234", "calladoctor")

# Creating tables
create_users_table = """
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(20),
    date_of_birth DATE,
    address VARCHAR(255),
    role ENUM('admin', 'doctor', 'patient') NOT NULL
);
"""

create_patients_table = """
CREATE TABLE IF NOT EXISTS Patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    fullname VARCHAR(100) NOT NULL,
    identification_number VARCHAR(12) NOT NULL,
    gender ENUM('male', 'female', 'other'),
    medical_history TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);
"""

create_clinics_table = """
CREATE TABLE IF NOT EXISTS Clinics (
    clinic_id INT AUTO_INCREMENT PRIMARY KEY,
    clinic_name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    clinic_license BLOB NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE
);
"""

create_doctors_table = """
CREATE TABLE IF NOT EXISTS Doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    fullname VARCHAR(100) NOT NULL,
    clinic_id INT NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    license_photo BLOB NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (clinic_id) REFERENCES Clinics(clinic_id) ON DELETE CASCADE
);
"""

create_appointments_table = """
CREATE TABLE IF NOT EXISTS Appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    clinic_id INT NOT NULL,
    doctor_id INT,
    appointment_date DATETIME NOT NULL,
    appointment_type VARCHAR(50),
    status ENUM('pending', 'accepted', 'rejected', 'completed', 'cancelled') DEFAULT 'pending',
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (clinic_id) REFERENCES Clinics(clinic_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id) ON DELETE SET NULL
);
"""

create_prescriptions_table = """
CREATE TABLE IF NOT EXISTS Prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    doctor_id INT NOT NULL,
    patient_id INT NOT NULL,
    medication TEXT NOT NULL,
    notes TEXT,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE
);
"""

create_notifications_table = """
CREATE TABLE IF NOT EXISTS Notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    notification_type ENUM('appointment', 'medical', 'general') NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);
"""

# Execute table creation queries in the correct order
execute_query(connection, create_users_table)
execute_query(connection, create_clinics_table)
execute_query(connection, create_patients_table)
execute_query(connection, create_doctors_table)
execute_query(connection, create_appointments_table)
execute_query(connection, create_prescriptions_table)
execute_query(connection, create_notifications_table)