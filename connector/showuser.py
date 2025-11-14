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

def fetch_users(connection):
    fetch_users_query = "SELECT * FROM Users"
    cursor = connection.cursor()
    try:
        cursor.execute(fetch_users_query)
        users = cursor.fetchall()
        print("Users retrieved successfully")
        return users
    except Error as e:
        print(f"The error '{e}' occurred")
        return None

# Replace with your own database connection details
connection = create_connection("localhost", "root", "calladoctor1234", "calladoctor")

users = fetch_users(connection)
if users:
    for user in users:
        print(user)

connection.close()
