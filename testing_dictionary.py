import mysql.connector
from tabulate import tabulate
import sqlite3

mydb = mysql.connector.connect(host="localhost", user="root", password="hola123", database="nli_db")

mycursor = mydb.cursor()

mycursor.execute("SELECT country, score FROM location")
myresult = mycursor.fetchall()
print(tabulate(myresult, headers=['country', 'score'], tablefmt='psql'))

dict = {
    "age": 89,
    "loc": "Spain",
    "medical_cond": "flu",
    "smoker": True,
    "pregnant": False
}
# Age
if 0 <= dict.get("age") <= 69:
    mycursor.execute("select score from age where agecol=1")
    score1 = [x[0] for x in mycursor.fetchall()]
    print("your age risk (", dict.get("age"), ") is", score1)

if 70 <= dict.get("age") <= 100:
    mycursor.execute("select score from age where agecol=100")
    score1 = [x[0] for x in mycursor.fetchall()]
    print("your age risk (", dict.get("age"), ") is", score1)

# mycursor.execute("SELECT score FROM location WHERE country='Ecuador'")
# score_country = [x[0] for x in mycursor.fetchall()]
# print("your country risk is", score_country)
#

# Country
mycursor.execute("SELECT score FROM location WHERE country=%s", (dict.get("loc"),))
data = [x[0] for x in mycursor.fetchall()]

if data:
    print("your country risk (", dict.get("loc"), ") is", data)

else:
    print("Location does not exist")

# Medical Condition
mycursor.execute("SELECT score FROM medical_cond WHERE disease=%s", (dict.get("medical_cond"),))
data = [x[0] for x in mycursor.fetchall()]

if data:
    print("your medical condition risk (", dict.get("medical_cond"), ") is", data)

else:
    print("Medical Condition does not exist")

# Smoker
if dict.get("smoker")==True:
    mycursor.execute("select score from smoker where smokercol='True'")
    score2 = [x[0] for x in mycursor.fetchall()]
    print("your smoker risk (", dict.get("smoker"), ") is", score2)

else:
    mycursor.execute("select score from smoker where smokercol='False'")
    score2 = [x[0] for x in mycursor.fetchall()]
    print("your smoker risk (", dict.get("smoker"), ") is", score2)

# Pregnant
if dict.get("pregnant"):
    mycursor.execute("select score from pregnant where pregnantcol='True'")
    score3 = [x[0] for x in mycursor.fetchall()]
    print("your pregnant risk (", dict.get("pregnant"), ") is", score1)

else:
    mycursor.execute("select score from pregnant where pregnantcol='False'")
    score3 = [x[0] for x in mycursor.fetchall()]
    print("your pregnant risk (", dict.get("pregnant"), ") is", score1)

