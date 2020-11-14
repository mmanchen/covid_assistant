import speech_recognition as srg
import pyttsx3


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

if rec.recognize_google(paudio)== "hello":
    engine = pyttsx3.init()
    engine.say('I can give you your risk category. do you want to try?.')
    engine.runAndWait()