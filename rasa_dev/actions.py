from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType
import openai

import pandas as pd
import requests
import os
from  dotenv import load_dotenv, find_dotenv
find_dotenv()
load_dotenv()
import boto3
import numpy as np
import json
import ast
from tqdm import tqdm
import time
import string
import chardet

#############################################################################################################################################################################################################
#############################################################################################################################################################################################################
#############################################################################################################################################################################################################
#############################################################################################################################################################################################################

class ActionCheckAge(Action):
    def name(self) -> Text:
        return "action_check_age"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global age
        recipe = pd.read_csv(r"recipe.csv", encoding = 'latin-1')
        recipe['age'] = recipe['age'].astype(str)
        age_list = recipe['age'].to_list()
        age = str(tracker.get_slot("age"))
        age_is_valid = age in age_list
        return [SlotSet("age_is_valid", age_is_valid)]
    

class ActionCheckGoodbye(Action):

    def name(self) -> str:
        return "action_check_goodbye"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_input = tracker.get_slot("any_question")
        if 'bye' in user_input:
            return [SlotSet("user_said_goodbye", True)]
        return [SlotSet("user_said_goodbye", False)]



class ActionGetRecipe(Action):
    def name(self) -> Text:
        return "action_get_recipe"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        food_category = str(tracker.get_slot("food_category"))
        lactose_intolerant = tracker.get_slot("lactose_intolerant")
        
        file_path = r"C:\Users\gokul\Downloads\rasa_dev\recipesss.csv"
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        recipe = pd.read_csv(file_path, encoding=encoding)
       

        if(lactose_intolerant==True):
            lactose_intolerant=1
        else:
            lactose_intolerant=0


        recipe.to_csv(r"C:\Users\gokul\Downloads\rasa_dev\details_of_recipe.csv",index=False)

        all_text = recipe.to_string()
        print(recipe.shape)
        print(len(all_text))
        prompt = f"""
        the data of the recipe with details 
        
        {all_text} and my child age is {age} and lactose {lactose_intolerant} and food session is {food_category}
        
        please select the good recipe from this data and give details of recipe name , description , incredients , steps , nutrients present .
        """
       
        if True:
        
        

            response = openai.ChatCompletion.create(
                # model="gpt-3.5-turbo",
                model="gpt-4o",
                temperature=0.0,
                top_p=0.0001,
                messages=[
                    {"role": "system", "content": "You behave like a chatbot and give recipe details to user."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the CSV formatted response
            csv_data = response['choices'][0]['message']['content']

     
        
        print(csv_data)
        recommended_recipe=csv_data
        rephrased_recipe=recommended_recipe

        input_value = "can you suggest food?"
        response_value = recommended_recipe

        # Read the existing CSV file into a DataFrame
        file_path = r"C:\Users\gokul\Downloads\rasa_dev\prev_response.csv"
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        prev_res = pd.read_csv(file_path, encoding=encoding)
        # Create a new DataFrame for the new row
        new_data = {'input': input_value, 'response': response_value}
        new_row = pd.DataFrame([new_data])
        prev_res = pd.concat([prev_res, new_row], ignore_index=True)
 
      
        # Save the updated DataFrame back to the CSV file
        prev_res.to_csv(r"C:\Users\gokul\Downloads\rasa_dev\prev_response.csv", index=False)
        return [SlotSet("recommended_recipe", recommended_recipe), SlotSet("rephrased_recipe", rephrased_recipe)]





    

class ActionHandleFallbackQuestion(Action):
    def name(self) -> Text:
        return "action_handle_fallback_question"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_input =tracker.get_slot("any_question")
        print(user_input)
        file_path=r"C:\Users\gokul\Downloads\rasa_dev\details_of_recipe.csv"
        recipe = pd.read_csv(file_path, encoding='latin1')

        prev_response=pd.read_csv(r"C:\Users\gokul\Downloads\rasa_dev\prev_response.csv", encoding='latin1')

        
        prev_data=prev_response.to_string()
        all_text = recipe.to_string()


        prompt = f"""
        the data of the recipe with details 
        
        {all_text}   and previous context of chat gives this recipe {prev_data} and my wquestion is {user_input}
        
        please select the good recipe from this data other than previous recipe and give details of recipe name , description , incredients , steps , nutrients present .
        """
       
        if True:
            response = openai.ChatCompletion.create(
                # model="gpt-3.5-turbo",
                model="gpt-4o",
                temperature=0.0,
                top_p=0.0001,
                messages=[
                    {"role": "system", "content": "You behave like a chatbot and give recipe details to user."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the CSV formatted response
            csv_data = response['choices'][0]['message']['content']

        

     
        another_recipe=csv_data
        prev_response=pd.read_csv(r"C:\Users\gokul\Downloads\rasa_dev\prev_response.csv")
        new_data = {'input': user_input, 'response': csv_data}
        new_row = pd.DataFrame([new_data])
        prev_response = pd.concat([prev_response, new_row], ignore_index=True)
 

        prev_response.to_csv(r"C:\Users\gokul\Downloads\rasa_dev\prev_response.csv",index=False)
        return [SlotSet("another_recipe", another_recipe)]

       



    



