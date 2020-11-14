import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="root", password="hola123", database="nli_db")

mycursor = mydb.cursor()

age = input("Enter your age:\n")

age = int(age)

if 0 <= age <= 25:
    mycursor.execute("select score from age where agecol=25")
    score1 = [x[0] for x in mycursor.fetchall()]
    print("your age risk score is", score1)

if 26 <= age <= 65:
    mycursor.execute("select score from age where agecol=65")
    score1 = [x[0] for x in mycursor.fetchall()]
    print("your age risk score is", score1)

if 66 <= age <= 79:
    mycursor.execute("select score from age where agecol=66")
    score1 = [x[0] for x in mycursor.fetchall()]
    print("your age risk score is", score1)

if 80 <= age <= 100:
    mycursor.execute("select score from age where agecol=100")
    score1 = [x[0] for x in mycursor.fetchall()]
    print("your age risk score is", score1)

disease = input("(Answer YES or NO) Do you have diabetes, respiratory diseases, or lung diseases:\n")

if disease == "YES":
    disease_type = input("Which of these do you have: diabetes, respiratory, lung:\n")
    if disease_type == "diabetes":
        mycursor.execute("select score from medical_cond where disease='diabetes'")
        score2 = [x[0] for x in mycursor.fetchall()]
        print("your disease risk score is", score2)


else:
    mycursor.execute("select score from medical_cond where disease='none'")
    score2 = [x[0] for x in mycursor.fetchall()]
    print("your disease risk score is", score2)

risk = input("(Answer YES or NO) Do you want to know your overall risk?:\n")

if risk == "YES":
    list_results = score1+score2
    print("these are the results of the scores obtained ", list_results)
    overall_score = score1[0] + score2[0]
    print("this is your overall score",overall_score)

if 0 <= age <= 3:
    print("you belong to the risk group 4: there are no high risks for you but you should still take precautions")


# mycursor.execute("select score from age where agecol=100")
# x = [x[0] for x in mycursor.fetchall()]
# print("The score for this age is:", x)
#
# mycursor.execute("select score from age where agecol=25")
# x = [x[0] for x in mycursor.fetchall()]
# print("The score for this age is:",x)
#
# mycursor.execute("select score from medical_cond where disease='diabetes'")
# x = [x[0] for x in mycursor.fetchall()]
# print("The score for this disease is:",x)
#
# for i in mycursor:
#     print(i)

