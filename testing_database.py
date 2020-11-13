import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="root", password="hola123", database="nli_db")

mycursor = mydb.cursor()

mycursor.execute("select * from medical_cond")

for i in mycursor:
    print(i)
