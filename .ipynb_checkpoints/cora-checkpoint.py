import os
import sys
import numpy as np
from datetime import date
import mysql.connector
from tabulate import tabulate
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

        #Here the subject is missing but it needs to be added
        if (have_age == True) and (have_loc == True):
            DM_vec[1] = 1
            break
        else:
            print(" I will need to ask you a few more questions to fill the query up")

            if (Frame['age'] == 0) or (f.is_number(Frame['age']) == False):
                print("Sorry I didn't quite get your/her/his age")
                input_text = f.wait_input()
                Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
                response= f.respond_to_intents(Intents,Frame)
                print(response)
                Intents = f.init_intent()
            else:
                have_age =True


            #Here we need to check if the country is in our list
            
            check_loc = f.is_country(Frame['live_in'])
            
            if (Frame['live_in'] == 0):
                print("Where do you live?")
                input_text = f.wait_input()
                Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
                response= f.respond_to_intents(Intents,Frame)
                print(response)
                Intents = f.init_intent()
            elif check_loc == False:
                print("Sorry the location you specify is either not a country or is not in my list")
                input_text = f.wait_input()
                Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
                response= f.respond_to_intents(Intents,Frame)
                print(response)
                Intents = f.init_intent() 
            else:
                have_loc = True


    #############################################
    # Part where you extract the info from the database and fill in the profile

    filled_slots= f.check_filled_slots(Frame)

    filled_slots_scores = f.check_database(filled_slots)
    
    risk_level = f.sum_risk(filled_slots_scores)

    print("Your total risk index is: {}".format(risk_level))
    #############################################


    #for now it tries to fill all the slots, maybe it would be better if it's more flexible
    while DM_vec[2]==0:


        empty_slots= f.check_empty_slots(Frame)


        if len(empty_slots) == 0:
            DM_vec[2]=1

        else: 
            for item in empty_slots:
                print("I need information about {}".format(item))
                input_text = f.wait_input()
                Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
                response= f.respond_to_intents(Intents,Frame)
                print(response)
                Intents = f.init_intent()


     #############################################
    # Part where you extract the info from the database and fill in the profile
    #!!!!!If we did manage to get more information:
    # here we would repeat the connection to the database and the profiling, otherwise we continue
    
    empty_slots_2= f.check_empty_slots(Frame)
    if empty_slots_2 != empty_slots:
        filled_slots= f.check_filled_slots(Frame)

        filled_slots= f.check_filled_slots(Frame)

        filled_slots_scores = f.check_database(filled_slots)
    
        risk_level = f.sum_risk(filled_slots_scores)

        print("Your total risk index is: {}".format(risk_level))
        
    #############################################

    
    #This part tries to see if we need another profiling or we say goodbye
    while DM_vec[3] == 0:
        print('Would you like to know the profile of another person? Maybe your sister, your uncle..')

        input_text = f.wait_input()
        Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
        

        if Intents['accept'] == True:

            print('Lets start another query then')
            DM_vec[3] = 1
            #HERE WE NEED TO FIND A WAY TO GO BACK TO THE START: we need a higher level while loop to control this flow

        if (Intents['deny'] == True) or (Intents['goodbye']== True):

            #print('As you want.')
            conversation = False
            DM_vec[3] = 1
            
        response= f.respond_to_intents(Intents,Frame)
        print(response)
        iteration += 1