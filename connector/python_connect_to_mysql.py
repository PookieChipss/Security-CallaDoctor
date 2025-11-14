import mysql.connector

conn=mysql.connector.connect(host='localhost',username='root',password='calladoctor1234',database='calladoctor')
my_cursor=conn.cursor()

conn.commit()
conn.close()

print("Connection succesfully created!")