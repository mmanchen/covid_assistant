import os
import sys
import numpy as np
from datetime import date


#Better to define most functions outside and call them(easier)
sys.path.append('../modules/')
import functions as f

f.prepare_pipeline()

#start code for Cora DM


#Define the stages of the dialogue manager with a vector and 0,1 so we have memory on which stage are we and what things
#have been done before (I thought it could be useful)

DM_vec=[0,0,0]

#Define intents dictionary: this dictionary has to be initialized everytime ( we use a function to initialize it)
Intents = f.init_intent()
    
#Define  frame dictionary: this dictionary accumulates the info during the whole conversation

Frame= f.init_frame()

#IDEA: create a function that notices during the whole conversation if any particular or important intent is happening??
#      not only look for intent when we expect one.


# Greeting part
while DM_vec[0] == 0:
    
    print('Cora presentation and greeting')
    input_text = f.wait_input()
    Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
    print(Intents)
    
    if Intents['ask_help'] == True:
        print('Of course I will help!')
    
    if Intents['greeting'] == True:
        print('Nice to meet you')
        #Idea: if neuralcoref works it could say the name if you gave your name!
    
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
            Intents = f.init_intent()
        else:
            have_age =True


        #Here we need to check if the country is in our list
        if (Frame['live_in'] == 0):
            print(" Sorry the location you specify is either not a country or is not in our list")
            input_text = f.wait_input()
            Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
            Intents = f.init_intent()
        else:
            have_loc = True
            
            
#############################################
# Part where you extract the info from the database and fill in the profile

for k,v in Frame.items():
    if  (type(v)!= list) and ((v != 0) or (v == True)):
        print('slots that are filled:', k, 'values:', v)
    elif (type(v)== list) and (len(v) != 0):
        print('slots that are filled:', k, 'values:', v)
        
#Check database

print("Your profile is...")
#############################################


#for now it tries to fill all the slots, maybe it would be better if it's more flexible
while DM_vec[2]==0:
    
    
    ######## This should be turned into a function??
    empty_slots=[]
    for k,v in Frame.items():
        if  (type(v)!= list) and (type(v)!= bool) and (v == 0) and (k != 'pronoun') and (k != 'name'):
            empty_slots.append(k)
            print('slots that are NOT filled:', k)
            if k == 'smoker':
                print(v)
        elif (type(v)== list) and (len(v) == 0) and (k != 'med_cond'):
            empty_slots.append(k)
            print('slots that are NOT filled:', k)
    
            
    if len(empty_slots) == 0:
        DM_vec[2]=1
        
    else: 
        for item in empty_slots:
            print("I need information about {}".format(item))
            input_text = f.wait_input()
            Frame, Intents = f.intent_slot_filling(input_text,Frame,Intents)
            Intents = f.init_intent()
            

#!!!!!If we did manage to get more information:
# here we would repeat the connection to the database and the profiling, otherwise we continue

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
        
        print('As you want. I hope I see you soon. Stay safe!')
        DM_vec[3] = 1
    
    