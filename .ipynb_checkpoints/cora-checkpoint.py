import os
import sys
import numpy as np
from datetime import date
import mysql.connector
from tabulate import tabulate
import random

mydb = mysql.connector.connect(host="localhost", user="root", password="hola123", database="nli_db")
mycursor = mydb.cursor()


#Better to define most functions outside and call them(easier)
sys.path.append('../modules/')
import functions as f

f.prepare_pipeline()

#start code for Cora DM

#IDEA: create a function that notices during the whole conversation if any particular or important intent is happening??
#      not only look for intent when we expect one.

#this checks if the conversation ends or if the whole process starts again
conversation = True

#This checks how many profiles are done
iteration=0

while conversation == True:
    
    #Define the stages of the dialogue manager with a vector and 0,1 so we have memory on which stage are we and what things
    #have been done before (I thought it could be useful)

    DM_vec=[0,0,0,0]
    
    #Define intents dictionary: this dictionary has to be initialized everytime ( we use a function to initialize it)
    Intents = f.init_intent()
    
    #Define  frame dictionary: this dictionary accumulates the info during the whole conversation

    Frame= f.init_frame()

    # Greeting part
    while DM_vec[0] == 0:
        
        if iteration<1:
            print(""" Hello! I'm CORA, the COvid Risk Assistant. If you give me a profile with information about you,
            your loved ones or someone you worry about, I can give you the risk profile of developing complications 
            from COVID-19 along with some recommendations to stay safe. 
            You know what they say.. prevention is better than the cure!""")
        elif iteration>=1:
            print('Tell me about the new person you want to profile.')
            
        input_text = f.wait_input()
        Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
        print(Intents)

        response= f.respond_to_intents(Intents,Frame)
        print(response)
            

        DM_vec[0] = 1


    #Second stage: where the required slots are filled    
    while DM_vec[1]== 0:

        have_age= False
        have_loc = False

        if (Frame['age'] != 0) and (f.is_number(Frame['age']) == True):
            have_age = True

        #Here we need to check if the country is in our list
        if (Frame['live_in'] != 0):
            have_loc = True

        responses1 = []
        responses2 = []
        #Here the subject is missing but it needs to be added
        if (have_age == True) and (have_loc == True):
            DM_vec[1] = 1
            break
            
        else:
            resp1= 'I will need to ask you a few more questions to fill the query up...'
            resp2 = 'The profile needs some extra required information...'
            resp3 = "I'm missing some information that is vital in order to provide this service properly..."
            responses1.append(random.choice([resp1,resp2,resp3]))
            responses2.append(random.choice([resp1,resp2,resp3]))
            

        if (Frame['age'] == 0) or (f.is_number(Frame['age']) == False):
            resp1= "Let's start with age, could you provide this information?"
            resp2 = "Age is important for this profiling, please provide this information."
            if Frame['she'] == True:
                resp4 = 'How old is she?'
            elif Frame['he'] == True:
                resp4 = 'How old is he?
            elif Frame['they'] == True:
                resp4 = 'How old are they, more or less?
            elif Frame['you'] == True:
                resp4 = 'How old are you?
            elif (Frame['she']==False) and (Frame['he']==False) and (Frame['they']==False) and (Frame['you']==False):
                resp4 = "Without the age I'm sorry but I can't do much."
            responses1.append(random.choice([resp1,resp2,resp4]))
            response = ''.join(responses1)
            print(response)
            input_text = f.wait_input()
            Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
            response_int= f.respond_to_intents(Intents,Frame)
            if len(response_int) >0:
                print(response_int)
            Intents = f.init_intent()
        else:
            have_age =True


        #Here we need to check if the country is in our list
            
        #mycursor.execute("SELECT score FROM location WHERE country=%s", location)
        #data = [x[0] for x in mycursor.fetchall()]
        data= 1
        if data:
            is_country= True
        else:
            is_country =False
                
            
        if (Frame['live_in'] == 0):
            resp1= "The location is important to know in order to assess the location risk!"
            resp2 = "I would need to know the country in order to adapt the profiling to the current risk"
            if Frame['she'] == True:
                resp4 = 'Where does she live?'
            elif Frame['he'] == True:
                resp4 = 'Where does he live?'
            elif Frame['they'] == True:
                resp4 = 'Where do they live?'
            elif Frame['you'] == True:
                resp4 = 'Where do you live?'
            elif (Frame['she']==False) and (Frame['he']==False) and (Frame['they']==False) and (Frame['you']==False):
                resp4 = "In which country are we assesing the risk?"
            responses2.append(random.choice([resp1,resp2,resp4]))
            response = ''.join(responses2)
            print(response)
            responses2 = [responses2[0]]
            input_text = f.wait_input()
            Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
            response_int= f.respond_to_intents(Intents,Frame)
            if len(response_int) >0:
                print(response_int)
            Intents = f.init_intent()
        elif (Frame['live_in'] != 0) and (is_country == False):
            resp1= "Oh sorry! Maybe I forgot to say that the location needs to be a country!"
            resp2 = "Hm.. I can't find this location in my database. Could you specify the country?"
            resp3 = "I got a little bit lost, which country is it?"
            responses2.append(random.choice([resp1,resp2,resp3]))
            response = ''.join(responses2)
            print(response)
            responses2 = [responses2[0]]
            input_text = f.wait_input()
            Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
            response_int= f.respond_to_intents(Intents,Frame)
            if len(response_int) >0:
                print(response_int)
            Intents = f.init_intent() 
        else:
            have_loc = True


    #############################################
    # Part where you extract the info from the database and fill in the profile

    filled_slots= f.check_filled_slots(Frame)

    dict = filled_slots
    #Check database

    if 0 <= dict.get("age") <= 69:
        mycursor.execute("select score from age where agecol=1")
        score1 = [x[0] for x in mycursor.fetchall()]
        print("your age risk (", dict.get("age"), ") is", score1)

    if 70 <= dict.get("age") <= 100:
        mycursor.execute("select score from age where agecol=100")
        score1 = [x[0] for x in mycursor.fetchall()]
        print("your age risk (", dict.get("age"), ") is", score1)

        # Country
    mycursor.execute("SELECT score FROM location WHERE country=%s", (dict.get("loc"),))
    data = [x[0] for x in mycursor.fetchall()]

    if data:
        print("your country risk (", dict.get("loc"), ") is", data)

    else:
        print("Location does not exist")

    # Smoker
    if dict.get("smoker")==True:
        mycursor.execute("SELECT score FROM smoker where smokercol='True'")
        score2 = [x[0] for x in mycursor.fetchall()]
        print("your smoker risk (", dict.get("smoker"), ") is", score2)

    else:
        mycursor.execute("select score from smoker where smokercol='False'")
        score2 = [x[0] for x in mycursor.fetchall()]
        print("your smoker risk (", dict.get("smoker"), ") is", score2)

    # Pregnant
    if dict.get("pregnant")==True:
        mycursor.execute("select score from pregnant where pregnantcol='True'")
        score3 = [x[0] for x in mycursor.fetchall()]
        print("your pregnant risk (", dict.get("pregnant"), ") is", score3)

    else:
        mycursor.execute("select score from pregnant where pregnantcol='False'")
        score3 = [x[0] for x in mycursor.fetchall()]
        print("your pregnant risk (", dict.get("pregnant"), ") is", score3)

    med_score  = np.sum(Frame['med_cond_risk'])
    list_results = score1 + data + score2 + score3 + [med_score]
    print("these are the results of the scores obtained ", list_results)
    overall_score = score1[0] + data[0] + score2[0] + score3[0] + med_score
    print("The total risk index is", overall_score)

        
    resp_r = []
    if Frame['she'] == True:
        resp4 = 'She belongs'
    if Frame['he'] == True:
        resp4 = 'He belongs
    if Frame['they'] == True:
        resp4 = 'They belong'
    if Frame['you'] == True:
        resp4 = 'You belong'
    if resp4:
        resp_r.append(resp4)
    else:
        resp_r.append('The profile belongs')
                
    if overall_score == 0:
        resp_risk = ("to the risk group 1: there are no risks, but that doesn’t mean you can’t have "
                  "bad luck, be careful!")
        resp_r.append(resp_risk)
        print(''.join(resp_r))
        print("Wear a mask when interacting with others, try to limit your in-person interactions, keep distance "
                  "when you are near other people, wash your hands often.")

    if 1 <= overall_score <= 2:
        resp_risk = ("to the risk group 2: there are low risks but should still take precautions")
        resp_r.append(resp_risk)
        print(''.join(resp_r))
        print("Wear a mask when interacting with others, try to limit your in-person interactions, keep distance "
                  "when you are near other people, wash your hands often, reduce your stay in public spaces, "
                  "avoid peak hours, ventilate your home to keep the air fresh.")

    if 3 <= overall_score <= 4:
        resp_risk = (" to the risk group 3: there is a moderate risk and should be cautious.")
        resp_r.append(resp_risk)
        print(''.join(resp_r))
        print("Wear a mask when interacting with others, try to limit your in-person interactions, only go out if "
                  "its really necessary, limit social activity, do not touch things that people you do not live with "
                  "have touched, including food and drinks, keep distance "
                  "when you are near other people, wash your hands often, reduce your stay in public spaces, "
                  "avoid peak hours, ventilate your home to keep the air fresh.")

    if overall_score >= 5:
        resp_risk = ("to the risk group 4:  there is a high risk and should take high precautions.")
        resp_r.append(resp_risk)
        print(''.join(resp_r))
        print("Wear a mask when interacting with others, try to do shopping online or ask family to collect "
                  "shopping for you, work from home if possible, wash hands for at least 20 seconds, try to stay at "
                  "least 2 metres away from anyone you do not live with,  try to limit your in-person interactions, "
                  "only go out if "
                  "its really necessary, limit social activity, do not touch things that people you do not live with "
                  "have touched, including food and drinks, keep distance "
                  "when you are near other people, wash your hands often, reduce your stay in public spaces, "
                  "avoid peak hours, ventilate your home to keep the air fresh.")


    #############################################


    j=0
    #for now it tries to fill all the slots, maybe it would be better if it's more flexible
    while DM_vec[2]==0:


        empty_slots= f.check_empty_slots(Frame)


        if len(empty_slots) == 0:
            DM_vec[2]=1

        if j== 0:
            intro = []
            if Frame['she'] == True:
                pron = 'her'
            elif Frame['he'] == True:
                pron = 'his'
            elif Frame['they'] == True:
                prin= 'their'
            elif Frame['you'] == True:
                pron= 'your'
            elif (Frame['she']==False) and (Frame['he']==False) and (Frame['they']==False) and (Frame['you']==False):
                pron= 'the'
                
            part1 = "Let's see, at the moment we have that {} age is {} years old and {} live(s) in {}, ".format(pron,Frame['age'],pron,Frame['live_in'])
            intro.append(part1)

            if type(Frame['smoker']) == bool:
                if Frame['smoker'] == True:
                    part3 = "smoking is factor, "
                    intro.append(part3)
                if Frame['smoker'] == False:
                    part3 = "smoking is not a factor, "
                    intro.append(part3)

            if len(Frame['med_cond_risk']) >0:
                part4 = "there also are certain medical conditions that sum up the risk to {}, ".format(med_score)
                intro.append(part4)

            part2 =""" and that is all...with this information we found that the risk is {}. Maybe we could add some information in order to get a more complete profile.""".format(overall_score)
            intro.append(part2)
            print(''.join(intro))


        if len(empty_slots)==1:
                responses2=[]
                resp1= "For example, one piece of information is missing."
                if Frame['she'] == True:
                    resp2 = 'Does she {}?'.format(empty_slots[0])
                elif Frame['he'] == True:
                    resp2 = 'Does he {}?'.format(empty_slots[0])
                elif Frame['they'] == True:
                    resp2 = 'Do they {}?'.format(empty_slots[0])
                elif Frame['you'] == True:
                    resp2 = 'Do you {}?'.format(empty_slots[0])
                elif (Frame['she']==False) and (Frame['he']==False) and (Frame['they']==False) and (Frame['you']==False):
                    resp2 = 'Does the person {}?'.format(empty_slots[0])
                responses2.append([resp1])
                responses2.append([resp2])
                response = ''.join(responses2)
                print(response)
                input_text = f.wait_input()
                Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
                response= f.respond_to_intents(Intents,Frame)
                print(response)
                if (empty_slots[0] =='smoke') and (Intents['accept'] ==True):
                    Frame['smoker'] =True
                if (empty_slots[0] =='smoke') and (Intents['deny'] ==True):
                    Frame['smoker'] =False
                if (Frame['she']==False) and (Frame['he']==False) and (Frame['they']==False) and (Frame['you']==False):
                    Frame['med_cond_risk'] =False
                Intents = f.init_intent()
        if len(empty_slots)==2:
                responses2=[]
                resp1= "I think this other information could also help:"
                if Frame['she'] == True:
                    resp2 = 'Does she {} or {}?'.format(empty_slots[0],empty_slots[1])
                elif Frame['he'] == True:
                    resp2 = 'Does he {} or {}??'.format(empty_slots[0],empty_slots[1])
                elif Frame['they'] == True:
                    resp2 = 'Do they {} or {}??'.format(empty_slots[0],empty_slots[1])
                elif Frame['you'] == True:
                    resp2 = 'Do you {} or {}??'.format(empty_slots[0],empty_slots[1])
                elif (Frame['she']==False) and (Frame['he']==False) and (Frame['they']==False) and (Frame['you']==False):
                    resp2 = 'Does the person {} or {}??'.format(empty_slots[0],empty_slots[1])
                responses2.append(resp1)
                responses2.append(resp2)
                response = ''.join(responses2)
                print(response)
                input_text = f.wait_input()
                Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
                response= f.respond_to_intents(Intents,Frame)
                empty_slots= f.check_empty_slots(Frame)    
                print(response)
                if (empty_slots[1] =='have any medical conditions') and (Intents['deny'] == True):
                    Frame['med_cond_risk'] =False
                if (empty_slots[0] =='smoke') and (Intents['deny'] ==True):
                    Frame['smoker'] =False
                if (len(empty_slots)==2) and (Intents['accept']== True):
                    print('Which of the two do you mean? I will ask again...')
                Intents = f.init_intent()

        j+=1
     #############################################
    # Part where you extract the info from the database and fill in the profile
    #!!!!!If we did manage to get more information:
    # here we would repeat the connection to the database and the profiling, otherwise we continue
    
    empty_slots_2= f.check_empty_slots(Frame)
    if empty_slots_2 != empty_slots:
    
        filled_slots= f.check_filled_slots(Frame)

        dict = filled_slots
        #Check database

        if 0 <= dict.get("age") <= 69:
            mycursor.execute("select score from age where agecol=1")
            score1 = [x[0] for x in mycursor.fetchall()]
            print("your age risk (", dict.get("age"), ") is", score1)

        if 70 <= dict.get("age") <= 100:
            mycursor.execute("select score from age where agecol=100")
            score1 = [x[0] for x in mycursor.fetchall()]
            print("your age risk (", dict.get("age"), ") is", score1)

            # Country
        mycursor.execute("SELECT score FROM location WHERE country=%s", (dict.get("loc"),))
        data = [x[0] for x in mycursor.fetchall()]

        if data:
            print("your country risk (", dict.get("loc"), ") is", data)

        else:
            print("Location does not exist")

        # Smoker
        if dict.get("smoker")==True:
            mycursor.execute("SELECT score FROM smoker where smokercol='True'")
            score2 = [x[0] for x in mycursor.fetchall()]
            print("your smoker risk (", dict.get("smoker"), ") is", score2)

        else:
            mycursor.execute("select score from smoker where smokercol='False'")
            score2 = [x[0] for x in mycursor.fetchall()]
            print("your smoker risk (", dict.get("smoker"), ") is", score2)

        # Pregnant
        if dict.get("pregnant")==True:
            mycursor.execute("select score from pregnant where pregnantcol='True'")
            score3 = [x[0] for x in mycursor.fetchall()]
            print("your pregnant risk (", dict.get("pregnant"), ") is", score3)

        else:
            mycursor.execute("select score from pregnant where pregnantcol='False'")
            score3 = [x[0] for x in mycursor.fetchall()]
            print("your pregnant risk (", dict.get("pregnant"), ") is", score3)
        
        if type(Frame['med_cond_risk'])!= bool:
            med_score  = np.sum(Frame['med_cond_risk'])
        else:
            med_score = 0
        list_results = score1 + data + score2 + score3+[med_score]
        print("these are the results of the scores obtained ", list_results)
        overall_score = score1[0] + data[0] + score2[0] + score3[0]+med_score
        print("The total risk index is", overall_score)

        resp_r = []
        if Frame['she'] == True:
            resp4 = 'She belongs'
        if Frame['he'] == True:
            resp4 = 'He belongs
        if Frame['they'] == True:
            resp4 = 'They belong'
        if Frame['you'] == True:
            resp4 = 'You belong'
        if resp4:
            resp_r.append(resp4)
        else:
            resp_r.append('The profile belongs')
                
        if overall_score == 0:
            resp_risk = ("to the risk group 1: there are no risks, but that doesn’t mean you can’t have "
                  "bad luck, be careful!")
            resp_r.append(resp_risk)
            print(''.join(resp_r))
            print("Wear a mask when interacting with others, try to limit your in-person interactions, keep distance "
                  "when you are near other people, wash your hands often.")

        if 1 <= overall_score <= 2:
            resp_risk = ("to the risk group 2: there are low risks but should still take precautions")
            resp_r.append(resp_risk)
            print(''.join(resp_r))
            print("Wear a mask when interacting with others, try to limit your in-person interactions, keep distance "
                  "when you are near other people, wash your hands often, reduce your stay in public spaces, "
                  "avoid peak hours, ventilate your home to keep the air fresh.")

        if 3 <= overall_score <= 4:
            resp_risk = (" to the risk group 3: there is a moderate risk and should be cautious.")
            resp_r.append(resp_risk)
            print(''.join(resp_r))
            print("Wear a mask when interacting with others, try to limit your in-person interactions, only go out if "
                  "its really necessary, limit social activity, do not touch things that people you do not live with "
                  "have touched, including food and drinks, keep distance "
                  "when you are near other people, wash your hands often, reduce your stay in public spaces, "
                  "avoid peak hours, ventilate your home to keep the air fresh.")

        if overall_score >= 5:
            resp_risk = ("to the risk group 4:  there is a high risk and should take high precautions.")
            resp_r.append(resp_risk)
            print(''.join(resp_r))
            print("Wear a mask when interacting with others, try to do shopping online or ask family to collect "
                  "shopping for you, work from home if possible, wash hands for at least 20 seconds, try to stay at "
                  "least 2 metres away from anyone you do not live with,  try to limit your in-person interactions, "
                  "only go out if "
                  "its really necessary, limit social activity, do not touch things that people you do not live with "
                  "have touched, including food and drinks, keep distance "
                  "when you are near other people, wash your hands often, reduce your stay in public spaces, "
                  "avoid peak hours, ventilate your home to keep the air fresh.")

    #############################################

        
    #This part tries to see if we need another profiling or we say goodbye
    while DM_vec[3] == 0:
        print('Would you like to know the profile of another person?')

        input_text = f.wait_input()
        Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
        

        if Intents['accept'] == True:

            print('Lets start another query then')
            DM_vec[3] = 1
            #HERE WE NEED TO FIND A WAY TO GO BACK TO THE START

        if (Intents['deny'] == True) or (Intents['goodbye']== True):

            #print('As you want.')
            conversation = False
            DM_vec[3] = 1
            
        response= f.respond_to_intents(Intents,Frame)
        print(response)
        print('I will be here if you need me again :)')
        iteration += 1