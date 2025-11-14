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

def execute_query(connection, query, data=None):
    cursor = connection.cursor()
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
        return cursor.lastrowid
    except Error as e:
        print(f"The error '{e}' occurred")
        return None

def insert_user(connection, username, password, email, phone_number, date_of_birth, address, role):
    insert_user_query = """
    INSERT INTO Users (username, password, email, phone_number, date_of_birth, address, role)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    user_data = (username, password, email, phone_number, date_of_birth, address, role)
    user_id = execute_query(connection, insert_user_query, user_data)
    return user_id

def insert_patient(connection, user_id, fullname, identification_number, gender, medical_history):
    insert_patient_query = """
    INSERT INTO Patients (user_id, fullname, identification_number, gender, medical_history)
    VALUES (%s, %s, %s, %s, %s)
    """
    patient_data = (user_id, fullname, identification_number, gender, medical_history)
    execute_query(connection, insert_patient_query, patient_data)

def insert_doctor(connection, user_id, fullname, clinic_id, is_available, license_photo):
    insert_doctor_query = """
    INSERT INTO Doctors (user_id, fullname, clinic_id, is_available, license_photo)
    VALUES (%s, %s, %s, %s, %s)
    """
    doctor_data = (user_id, fullname, clinic_id, is_available, license_photo)
    execute_query(connection, insert_doctor_query, doctor_data)

# Replace with your own database connection details
connection = create_connection("localhost", "root", "calladoctor1234", "calladoctor")

# Check for existing users and insert if they don't exist
def insert_unique_user(connection, username, password, email, phone_number, date_of_birth, address, role, fullname, additional_insert_function=None, additional_data=None):
    check_user_query = "SELECT user_id FROM Users WHERE email = %s"
    cursor = connection.cursor()
    cursor.execute(check_user_query, (email,))
    result = cursor.fetchone()
    if result:
        print(f"User with email {email} already exists.")
        return result[0]
    else:
        user_id = insert_user(connection, username, password, email, phone_number, date_of_birth, address, role)
        if additional_insert_function and user_id:
            additional_insert_function(connection, user_id, *additional_data)
        return user_id

# Insert admin user
admin_id = insert_unique_user(
    connection, "admin", "admin", "admin@example.com", "1234567890", "1980-01-01", "Admin Address", "admin", 
    "Admin Fullname"
)

# Insert doctor user
doctor_id = insert_unique_user(
    connection, "doctor", "doctor", "doctor@example.com", "1234567890", "1985-05-05", "Doctor Address", "doctor", 
    insert_doctor, ["Doctor Fullname", 1, True, b'dummy_license_photo_data']  # Replace with actual clinic_id and license photo data
)

# Insert patient user
patient_id = insert_unique_user(
    connection, "patient", "patient", "patient@example.com", "1234567890", "1990-10-10", "Patient Address", "patient", 
    insert_patient, ["Patient Fullname", "123456789012", "male", "No medical history"]
)

connection.close()