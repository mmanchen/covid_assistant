import spacy
import en_core_web_sm
from spacy.strings import StringStore,hash_string
from datetime import date
import numpy as np
import random
nlp = en_core_web_sm.load()

from spacy.matcher import Matcher
from spacy.tokens import Token,Span
import time

from threading import Thread


def sum_risk(filled_slots_score):
    
    total_sum= int(filled_slots_score['age_score'])+ int(filled_slots['loc_score'])+int(filled_slots['smoker_score'])
    total_sum= total_sum+ int(filled_slots['pregnant'])+int(filled_slots['medical_risk'])
    
    return total_sum
    

def respond_to_intents(Intents,Frame):
    
# remember Intents={'greeting': False, 'thank': False, 'accept': False,'deny':False,'goodbye': False, 'ask_help':False }
    responses = []
    name = Frame['name']
    
    if Intents['ask_help'] == True:
        responses.append(random.choice(['Of course I will help!','Sure!','I will be glad to help.']))

    if Intents['greeting'] == True:
        if name != 0:
            responses.append(random.choice(['Nice to meet you {}.'.format(name),'Hey {}!'.format(name)]))
        else:   
            responses.append(random.choice(['Nice to meet you.','Hey there!']))
    
    if Intents['thank']== True:
        if name != 0:
            responses.append(random.choice(['You are welcome {}'.format(name),'No problem{}'.format(name)]))
        else:   
            responses.append(random.choice(['You are welcome','anytime!','No problem.']))
            
    if Intents['accept']== True:
        
        responses.append(random.choice(['I see.','Alright!','Gotcha!']))
        
    if Intents['deny']== True:
        
        responses.append(random.choice(['Alright then.','I see...']))
        
    if Intents['goodbye']== True:
        if name != 0:
            responses.append(random.choice(['Goodbye {}!'.format(name),'Farewell {}.'.format(name),'Take care {}.'.format(name)]))
        else:   
            responses.append(random.choice(['Goodbye!','Farewell','Take care']))
    
    #print(responses)
    #responses = random.shuffle(responses)
    
    response = ''.join(responses)
        
    return response
    
    
    

def check_filled_slots(Frame):
    #Returns a dictionary of the filled slots in order to search the  database
    
    filled_slots = {}

    for k,v in Frame.items():
        if (k=='age') and (is_number(v) == True):
            filled_slots[k] = int(v)
        if (k=='live_in'):
            filled_slots['loc'] = v
        if (k=='med_cond_risk'):
            filled_slots['medical_risk'] = np.sum(v)
        if (k == 'med_cond') and ('pregnant' in s for s in v):
            filled_slots['pregnant'] = v
        if (k=='smoker') and (type(v) == bool):
            filled_slots['smoker'] = v

    #print('filled slots:', filled_slots)
    
    return filled_slots

def check_empty_slots(Frame):
    
    #returns a list of the empty slots
    
    empty_slots=[]
    for k,v in Frame.items():
        if  (type(v)!= list) and (type(v)!= bool) and (v == 0) and (k != 'pronoun') and (k != 'name'):
            empty_slots.append('smoke')
        elif (type(v)== list) and (len(v) == 0) and (k != 'med_cond'):
            empty_slots.append('have any medical conditions')
    
    return empty_slots

def wait_input():
    answer = None

    def check():
        time.sleep(25)
        if answer != None:
            return
        print("Are you there?")

    Thread(target = check).start()
    answer = input("Enter your sentence: ")
    
    return answer


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    

def init_intent():
    #Define intents dictionary: this dictionary has to be initialized everytime ( we can use a function to ini)
    Intents={'greeting': False, 'thank': False, 
          'accept': False,'deny':False,'goodbye': False, 'ask_help':False }
    return Intents
    
    


def init_frame():
    
    #Define  frame dictionary: this dictionary accumulates the info during the whole conversation
    # Note that smoker for 0 is that we don't know but if we don't ask we assume it is a no, if they say no it goes to False
    Frame={'age': 0,'smoker':0,'med_cond_risk':[],
           'med_cond':[],'live_in': 0,'date': date.today().strftime("%d/%m/%Y"), 'pronoun': 0,'name': 0,'she': False,'he':False,'they': False,'you': False}
    return Frame


def prepare_pipeline():
    
    #Defining the pipeline object that recognizes intent

    class Intent(object):
        name='Intent'

        def __init__(self,nlp):


            self.matcher = Matcher(nlp.vocab)

            greeting_1 = [{'lemma': {"REGEX":"(hello|hey|hi|hola)"}}]

            greeting_2 = [{'lemma': 'good','lemma':{"REGEX": "(morning|day|night|afternoon)"}}]

            thank_1 = [{'lemma': 'thank'},{'lemma': 'you','OP':'?'}]

            accept_1 = [{'lemma': {"REGEX":"(yes|alright|sure)"}}]

            accept_2 = [{'POS': 'PRON'},{'LEMMA':'do','OP':'?'},{'LEMMA': 'agree'}]
            
            accept_3 = [{'LEMMA':'yes'}]

            deny_1 = [{'LEMMA': 'no'},{'IS_PUNCT':True}]

            deny_2 = [{'POS':'PRON'},{'LEMMA':'do','OP':'?'}, {'LEMMA': 'not'},{'LEMMA':{"REGEX":"(want|agree|accept)"}}]
            deny_3 = [{'LEMMA': 'no'},{'LEMMA':'thank'}]
            deny_4 = [{'LEMMA': 'no'}]

            goodbye_1 = [{'LEMMA': 'good'},{'LEMMA': 'bye'}]

            goodbye_3 = [{'LOWER': 'good-bye'}]

            goodbye_2 = [{'LEMMA':'see','LEMMA':'you'},
                      {'LEMMA':'soon'}]

            ask_1 = [{'LOWER':{"REGEX":"(can|could)"},'LOWER':'you'},{'LEMMA':'help'},{'OP':'?'},{'IS_PUNCT': True,'OP':'?'}]
            
            ask_2 = [{'POS':'PRON'}, {'LEMMA': 'want'},
                     {'LOWER':'your', 'OP':'?'},
                     {'LOWER':{"REGEX":"(help|advice|tip|information)"},'OP':'?'}]
            
            ask_3 = [{'LOWER':{"REGEX":"(can|could)"},'LOWER':'you'},
                     {'LEMMA':{"REGEX":"(give|tell|explain)"}},
                     {'LOWER':'the','OP':'?'},
                     {'LOWER': 'risk'}]
            
            ask_4 = [{'POS':'PRON'},{'LEMMA':'need'},{'LEMMA':'help'}]
            



            self.matcher.add('greeting',[greeting_1,greeting_2])
            self.matcher.add('thank',[thank_1])
            self.matcher.add('Accept',[accept_1,accept_2])
            self.matcher.add('Deny',[deny_1,deny_2,deny_3,deny_4])
            self.matcher.add('Goodbye',[goodbye_1,goodbye_2,goodbye_3])
            self.matcher.add('Ask',[ask_1,ask_2,ask_3,ask_4])


            Token.set_extension("is_thanking",default=False)
            Token.set_extension("is_greeting",default=False)
            Token.set_extension("is_accepting",default=False)
            Token.set_extension("is_denying",default=False)
            Token.set_extension("is_goodbye",default=False)
            Token.set_extension("is_asking", default=False)




        def __call__(self,doc):
            matches = self.matcher(doc)
            for match_id,start,end in matches:        

                if match_id == hash_string("greeting"):
                    entity = Span(doc, start, end, label="smoker")
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:  # set values of token attributes
                        token._.set("is_greeting", True)

                if match_id == hash_string("thank"):
                    entity = Span(doc, start, end, label="thank")
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:  # set values of token attributes
                        token._.set("is_thanking", True)

                if match_id == hash_string("Accept"):
                    entity = Span(doc, start, end, label="accept")
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:  # set values of token attributes
                        token._.set("is_accepting", True)

                if match_id == hash_string("Deny"):
                    entity = Span(doc, start, end, label="deny")
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:  # set values of token attributes
                        token._.set("is_denying", True)

                if match_id == hash_string("Goodbye"):
                    entity = Span(doc, start, end, label="goodbye")
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:  # set values of token attributes
                        token._.set("is_goodbye", True)

                if match_id == hash_string("Ask"):
                    entity = Span(doc, start, end, label="asking")
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:  # set values of token attributes
                        token._.set("is_asking", True)

            return doc


    # Defining the pipeline object that recognizes the frame slots    

    class Framing(object):
        name='Framing'

        def __init__(self,nlp):


            self.matcher = Matcher(nlp.vocab)
            age_1 = [{'DEP': 'nsubj'},
                   {'LEMMA': 'be'},
                   {'LIKE_NUM': True},
                   {'LEMMA': 'year','OP':'?'},
                   {'ORTH': 'old','OP':'?'}]
            
            age_2= [{'LIKE_NUM': True}]

            smoke1 = [{'DEP': 'nsubj','OP':'?'},
                      {'LEMMA':'DO','OP':'?'},
                 {'LEMMA':'not','OP':'!'},
                 {'LEMMA':'smoke'}]
            smoke2 = [{'DEP': 'nsubj','OP':'?'},
               {'LEMMA': 'be'},
                {'LEMMA':'not','OP':'!'},
               {'POS': 'DET','OP':'?'},
               {'LEMMA': 'smoker'}]
            
            smoke1_n = [{'DEP': 'nsubj','OP':'?'},
                      {'LEMMA':'DO','OP':'?'},
                 {'LEMMA':'not'},
                 {'LEMMA':'smoke'}]
            
            smoke2_n = [{'DEP': 'nsubj','OP':'?'},
               {'LEMMA': 'be'},
                {'LEMMA':'not'},
               {'POS': 'DET','OP':'?'},
               {'LEMMA': 'smoker'}]

            subject1 = [{'DEP': 'nsubj'},
               {'LEMMA': 'be'},
               {'ENT_TYPE': 'PERSON'}]
            
            subject2 = [{'POS': 'PRON'},
               {'LOWER': 'name'},
               {'LEMMA': 'be'},
               {'ENT_TYPE': 'PERSON'}]
            
            subject4 = [{'POS': 'PRON'},
               {'LOWER': 'name'},
               {'LEMMA': 'be'},
               {'ENT_TYPE': 'PERSON'}]
            
            subject3 = [{'LOWER': 'my'},
                       {'POS': 'NOUN'},
                          {'ENT_TYPE': 'PERSON'},
                         {'LEMMA': 'be'}]
            
            she1 = [{'POS':'DET'}, {'LOWER': {"REGEX":"(mother|sister|girlfriend|aunt|grandma|grandmother|mum)"}}]
            she2 = [{'LOWER':'she'}]
            
            he1 = [{'POS':'DET'}, {'LOWER': {"REGEX":"(dad|father|grandpa|grandfather|uncle|boyfriend)"}}]
            #he2 = [{'LOWER':'he'}]
            
            they1 = [{'POS':'DET'}, {'LOWER': {"REGEX":"(grandparents|parents|cousins)"}}]
            they2 = [{'LOWER':{"REGEX":"(elders|youth|they)"}}]
            
            you1 =  [{'LOWER': 'my'},
               {'LOWER': 'name'},
               {'LEMMA': 'be'}]
            
            you2 =  [{'LOWER': 'i'},
               {'LEMMA': 'be'}]
            
            you3 =  [{'LOWER': 'i'},
               {'LEMMA': 'live'}]


            subject_p1 = [{'DEP':'nsubj'},{'POS': 'PRON'}]
            
            subject_p2 = [{'LOWER': 'my'},
                   {'POS': 'NOUN','ENT_TYPE': 'PERSON'},
                         {'LEMMA': 'be'}]

            live_in1 = [{'LOWER':'and','OP':'?'},
                {'DEP':'nsubj','OP':'?'},
                      {'LEMMA':'be'},
                      {'LOWER': 'from'},
                      {'ENT_TYPE':'GPE'}]
            
            live_in2 = [{'DEP':'nsubj','OP':'?'},
              {'LEMMA':'live'},
              {'LOWER': 'in'},
              {'ENT_TYPE':'GPE'}]
            
            live_in3 = [{'ENT_TYPE':'GPE'}]

            medical2_1 = [{'LOWER':'not','OP':'!'},
                          {'LOWER':{"REGEX":"(severe|bad|terrible|strong)"},'OP':'?'},
                          {'LOWER':{"REGEX":"(kidney|lung)"}},
                         {'LOWER':{"REGEX":"(disease|condition)"}}]

            medical2_2 = [{'LOWER':'not','OP':'!'},
                          {'LOWER':{"REGEX":"(severe|bad|terrible|strong)"}},
                          {'LOWER':{"REGEX":"(heart|lung)"}},
                         {'LOWER':{"REGEX":"(disease|condition)"}}]

            medical2_3 = [{'LEMMA':'have','OP':'?'},
                          {'LOWER':'not','OP':'!'},
                          {'LEMMA':'get','OP':'?'},
                          {'LOWER':{"REGEX":"(cancer|leukaemia|lymphoma|myeloma)"}}]

            medical2_4 = [{'LEMMA':'have','OP':'?'},
                          {'LOWER':'not','OP':'!'},
                          {'LEMMA':'get','OP':'?'},
                          {'LOWER':'cystic'},{'LOWER':'fibrosis'}]

            medical2_5 = [{'LEMMA':'have','OP':'?'},
                          {'LOWER':'not','OP':'!'},
                          {'LEMMA':'get','OP':'?'},
                          {'LOWER':'severe'},
                          {'LOWER':'asthma'}]

            medical2_6 = [{'LEMMA':'have','OP':'?'},
                          {'LOWER':'not','OP':'!'},
                          {'LEMMA':'get','OP':'?'},
                          {'LEMMA':'Down'},{'POS':'PART'},{'LOWER':'Syndrome'}]

            medical2_7 = [{'LOWER':{"REGEX":"(kidney|heart|liver|organ|lung|pancreas)"}},
                         {'LEMMA': 'transplant'}]

            medical2_8 = [{'LOWER':'not','OP':'!'},
                          {'LEMMA':{"REGEX":"(take|has)"}},
                          {'LOWER':'immunosuppressant'},
                         {'LOWER':{"REGEX":"(medicine|treatment)"}}]


            medical1_1 = [{'LEMMA':'have','OP':'?'},
                          {'LOWER':'not','OP':'!'},
                          {'LOWER':'severe','OP':'!'},
                         {'LOWER':{"REGEX":"(heart|liver|brain|lung)"}},
                         {'LOWER':{"REGEX":"(disease|condition)"}}]

            medical1_2 = [{'LEMMA':'have','OP':'?'},
                          {'LOWER':'not','OP':'!'},
                          {'LOWER':'multiple','OP':'?'},
                         {'LOWER':{"REGEX":"(obesity|bronchitis|diabetes|parkinson|sclerosis|diabetes)"}}]

            medical1_3 = [{'LEMMA':'have','OP':'?'},
                          {'LOWER':'not','OP':'!'},
                          {'LEMMA':'get','OP':'?'},
                          {'LOWER':'severe','OP':'!'},
                          {'LOWER':'asthma'}]

            medical1_4 = [{'LOWER':'not','OP':'!'},
                        {'LEMMA':'be','OP':'?'},
                          {'LOWER':'pregnant'}]

            medical1_5 = [{'LEMMA':'take','OP':'?'},
                          {'LOWER':'not','OP':'!'},
                          {'LOWER':'steroids'}]





            self.matcher.add('smoking pattern',[smoke1,smoke2])
            self.matcher.add('not smoking pattern',[smoke1_n,smoke2_n])
            self.matcher.add('Age',[age_1,age_2])
            self.matcher.add('Personal',[subject1,subject2,subject3])
            self.matcher.add('Pronoun',[subject_p1,subject_p2])
            self.matcher.add('Location',[live_in1,live_in2,live_in3])
            self.matcher.add('medium',[medical1_1,medical1_2,medical1_3,medical1_4,medical1_5])
            self.matcher.add('high',[medical2_1,medical2_2,medical2_3,medical2_4,medical2_5,medical2_6,medical2_7,medical2_8])
            self.matcher.add('she',[she1,she2])
            self.matcher.add('he',[he1])
            self.matcher.add('they',[they1,they2])
            self.matcher.add('you',[you1,you2,you3])

            Token.set_extension("is_age",default=False)
            Token.set_extension("is_smoker",default=False)
            Token.set_extension("is_notsmoker",default=False)
            Token.set_extension("is_name",default=False)
            Token.set_extension("is_pronoun",default=False)
            Token.set_extension("is_relative",default=False)
            Token.set_extension("is_living",default=False)
            Token.set_extension("has_med1", default=False)
            Token.set_extension("has_med2", default=False)
            Token.set_extension("is_she", default=False)
            Token.set_extension("is_he", default=False)
            Token.set_extension("is_they", default=False)
            Token.set_extension("is_you", default=False)


        def __call__(self,doc):
            matches = self.matcher(doc)

            for match_id,start,end in matches:
                if match_id == hash_string("Age"):
                    span = doc[start:end]  # The matched span
                    age = ([token for token in span.subtree if token.like_num][0])
                    age._.set("is_age",True)
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print('Age:', age)
                    #print(span)


                if match_id == hash_string("smoking pattern"):
                    entity = Span(doc, start, end, label="smoker")
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:  # set values of token attributes
                        token._.set("is_smoker", True)
                        
                if match_id == hash_string("not smoking pattern"):
                    entity = Span(doc, start, end, label="not smoker")
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:  # set values of token attributes
                        token._.set("is_notsmoker", True)

                if match_id == hash_string("Personal"):
                    entity = Span(doc, start, end)
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:# set values of token attributes
                        #print(token)
                        if token.ent_type_ == 'PERSON':
                            token._.set("is_name", True)

                if match_id == hash_string("Pronoun"):
                    entity = Span(doc, start, end)
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:# set values of token attributes
                        if token.dep_ == 'nsubj':
                            token._.set("is_pronoun", True)

                if match_id == hash_string("Location"):
                    entity = Span(doc, start, end)
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:# set values of token attributes
                        if token.ent_type_ == 'GPE':
                            token._.set("is_living", True)

                if match_id == hash_string("high"):
                    entity = Span(doc, start, end, label="high")
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:  # set values of token attributes
                        token._.set("has_med2", True)

                if match_id == hash_string("medium"):
                    entity = Span(doc, start, end, label="medium")
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:  # set values of token attributes
                        token._.set("has_med1", True)
                        
                if match_id == hash_string("she"):
                    entity = Span(doc, start, end, label="she")
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:  # set values of token attributes
                        token._.set("is_she", True)
                        
                if match_id == hash_string("he"):
                    entity = Span(doc, start, end, label="he")
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:  # set values of token attributes
                        token._.set("is_he", True)
                        
                if match_id == hash_string("they"):
                    entity = Span(doc, start, end, label="they")
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:  # set values of token attributes
                        token._.set("is_they", True)
                        
                if match_id == hash_string("you"):
                    entity = Span(doc, start, end, label="you")
                    span = doc[start:end]  # The matched span
                    string_id = nlp.vocab.strings[match_id] 
                    #print('pattern:',string_id)
                    #print(span)
                    for token in entity:  # set values of token attributes
                        token._.set("is_you", True)
                        
                

            return doc


    # Adds objects to the pipeline

    component= Framing(nlp)
    component_2 = Intent(nlp)

    nlp.add_pipe(component_2,last=True)

    nlp.add_pipe(component,last=True)


        
        

#Returns the dictionary of Intents and Frames for a given input

def intent_slot_filling(text,Frame,Intents):
    
    doc=nlp(text)

    #thank
    if not  ([(token.text) for token in doc if token._.is_thanking]):
        Intents['thank'] = False
    else:
        Intents['thank'] = True


    #greeting
    if not ([(token.text) for token in doc if token._.is_greeting]):
        Intents['greeting'] = False
    else:
        Intents['greeting'] = True

    #goodbye
    if not ([(token.text) for token in doc if token._.is_goodbye]):
        Intents['goodbye'] = False
    else:
        Intents['goodbye'] = True

    #accept
    if not ([(token.text) for token in doc if token._.is_accepting]):
        Intents['accept'] = False
    else:
        Intents['accept'] = True

    #deny
    if not ([(token.text) for token in doc if token._.is_denying]):
        Intents['deny'] = False
    else:
        Intents['deny'] = True


    #ask for help
    if not ([(token.text) for token in doc if token._.is_asking]):
        Intents['ask_help'] = False
    else:
        Intents['ask_help'] = True
        
    #Age
    age_slot = ([(token.text) for token in doc if token._.is_age])
    if age_slot:
        Frame['age'] = age_slot[0]


    #smoker
    if  ([(token.text) for token in doc if token._.is_smoker]):
        Frame['smoker'] = True
    
    #not smoker
    if ([(token.text) for token in doc if token._.is_notsmoker]):
        Frame['smoker'] = False



    #Location
    loc = ([(token.text) for token in doc if token._.is_living])
    if loc:
        Frame['live_in']  = loc[0]

    #Name

    name = ([(token.text) for token in doc if token._.is_name])
    if name:
        Frame['name']  = name[0]

    #Pronoun
    pronoun = ([(token.text) for token in doc if token._.is_pronoun])
    if pronoun:
        for item in pronoun:
            Frame['pronoun']  = item

    med_2 = ([(token.text) for token in doc if token._.has_med2])
    if med_2:
        Frame['med_cond_risk'].append(2)
        Frame['med_cond'].append(med_2)

    med_1 = ([(token.text) for token in doc if token._.has_med1])
    if med_1:
        Frame['med_cond_risk'].append(1)
        Frame['med_cond'].append(med_1)

        
    #she
    if  ([(token.text) for token in doc if token._.is_she]):
        Frame['she'] = True
        
    #she
    if  ([(token.text) for token in doc if token._.is_he]):
        Frame['he'] = True
        
    #she
    if  ([(token.text) for token in doc if token._.is_they]):
        Frame['they'] = True
        
    #she
    if  ([(token.text) for token in doc if token._.is_you]):
        Frame['you'] = True
    

    
    #print(text)
    print(Frame)
    #print(Intents)
    
    return Frame, Intents
    