import speech_recognition as srg
import pyttsx3
import mysql.connector
mydb = mysql.connector.connect(host="localhost", user="root", password="hola123", database="nli_db")
mycursor = mydb.cursor()

engine = pyttsx3.init()
newVoiceRate = 125
voices = engine.getProperty('voices')
engine.setProperty('rate',newVoiceRate)
engine.setProperty('voice', voices[1].id)
engine.say('hello.')
engine.runAndWait()


rec = srg.Recognizer()

with srg.Microphone() as source:
    print("speak now")
    paudio = rec.listen(source)
    print("GOTCHA!")


    print("test voice to text:" + rec.recognize_google(paudio))

    if rec.recognize_google(paudio) == "hello":
        print(""" Hello! I'm CORA, the COVID Risk Assistant. If you give me a profile with information about you, 
        your loved ones or someone you worry about, I can give you the risk profile of developing complications
        from COVID-19 along with some recommendations to stay safe.
        You know what they say.. prevention is better than the cure!""")
        engine.say("""" Hello! I'm CORA, the COVID Risk Assistant. If you give me a profile with information about you,
        your loved ones or someone you worry about, I can give you the risk profile of developing complications
        from COVID-19 along with some recommendations to stay safe.
        You know what they say.. prevention is better than the cure!""""")


print("What is your age?")
engine.say('what is your age?')
engine.runAndWait()

with srg.Microphone() as source:
    print("speak now")
    age = rec.listen(source)
    print("GOTCHA!")


    print("your age is:" + rec.recognize_google(age))

print("Where do you live?")
engine.say('Where do you live?')
engine.runAndWait()

with srg.Microphone() as source:
    print("speak now")
    loc = rec.listen(source)
    print("GOTCHA!")

    print("you live in :" + rec.recognize_google(loc))

print("Do you have any medical conditions?")
engine.say('Do you have any medical conditions')
engine.runAndWait()

with srg.Microphone() as source:
    print("speak now")
    med_cond = rec.listen(source)
    print("GOTCHA!")

    print("medical conditions :" + rec.recognize_google(med_cond))

    if rec.recognize_google(med_cond)=="yes":
        print("Which medical conditions do you have?")
        engine.say('Which medical conditions do you have?')
        engine.runAndWait()

        with srg.Microphone() as source:
            print("speak now")
            med_cond = rec.listen(source)
            print("GOTCHA!")

            print("medical conditions :" + rec.recognize_google(med_cond))




print("Do you smoke?")
engine.say('Do you smoke?')
engine.runAndWait()

with srg.Microphone() as source:
    print("speak now")
    smoker = rec.listen(source)
    print("GOTCHA!")

    print("smoker :" + rec.recognize_google(smoker))

print("Are you pregnant?")
engine.say('Are you pregnant?')
engine.runAndWait()

with srg.Microphone() as source:
    print("speak now")
    pregnant = rec.listen(source)
    print("GOTCHA!")

    print("pregnant :" + rec.recognize_google(pregnant))


# with srg.Microphone() as source:
#     if rec.recognize_google(paudio)== "hello":
#         engine = pyttsx3.init()
#         print("What is your age?")
#         engine.say("What is your age?")
#         age = rec.listen(source)
#         engine.runAndWait()
#         print("your age is:" + rec.recognize_google(age))


    # engine.say(""" Hello! I'm CORA, the COVID Risk Assistant. If you give me a profile with information about you,
    # your loved ones or someone you worry about, I can give you the risk profile of developing complications
    # from COVID-19 along with some recommendations to stay safe.
    # You know what they say.. prevention is better than the cure!""")
    engine.runAndWait()



