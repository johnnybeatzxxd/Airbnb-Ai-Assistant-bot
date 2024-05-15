import json
import random
from . import database
from . import airbnb
import datetime
import time
import requests
import os
import base64
from dotenv import load_dotenv
import traceback
load_dotenv()

gemini_api_key = os.environ.get('GeminiProKey')
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={}".format(gemini_api_key)
headers = {"Content-Type": "application/json",}


today = datetime.date.today()
year = today.year
month = today.month
day = today.day


function_descriptions = [
        {
            "name": "save_user_information",
            "description": "This function must be triggerd when customer provide their email and name. if the user provide one of them it should be saved instantly",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "save the name of the customer eg. anuar,yishak ...",
                    },
                    "email": {
                        "type": "string",
                        "description": "save the email of the customer eg. anuar@...,yishak@...",
                        },

                },
                "required": [],
            }
            },
        {
            "name": "off_topic",
            "description": "this function must be triggered when user prompt is not related to our service and business. eg. 'how to install requerments of script thats in text file','how to be good sells man?','how is a car made','how to cook a piza','whats inside car engine','What has a mouth but never speaks?'",
            "parameters": {
                "type": "object",
                "properties": {
                    "off_topic": {
                        "type": "string",
                        "description": "true or false",
                    }

                },
                "required": ["question didnt relate"],
            }
            },
            
        {
            "name": "include_image",
            "description": "this function must be triggered when you always talk about specific thing in our property. like about the kitchen bathroom bedroom...",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_of": {
                        "type": "string",
                        "description": "the image to send with your responses. It must be one of the following: [outdoor,house,bedroom,bathroom]. Otherwise, say i dont have an image, because the app will crash. choose one of them that matches with user question.",
                    }

                },
                "required": ["image_of"],
            }
        },
        
        
        {
            "name": "get_property_info",
            "description": "you will get the answer of any question about our property.",
            "parameters": {
                "type": "object",
                "properties": {
                    "information_needed": {
                        "type": "string",
                        "description": "The type of information requested. It must be one of the following: [title,description,price,availability,bedroom,location,rules,Safety & property]. Otherwise, the app will crash.",
                    },               

                },
                "required": ['information needed']
            }
            },
            {
            "name": "get_aminities_info",
            "description": "This function returns the information about a specific amenity. use ['All amenities'] to get all the amenities details at once.",
            "parameters": {
                "type": "object",
                "properties": {
                    "aminities": {
                        "type": "string",
                        "description": 'The name of the amenity. It must be one of the following: ["Bathroom", "Bedroom and laundry", "Essentials", "Entertainment", "Family", "Heating and cooling", "Home safety", "Internet and office", "Kitchen and dining", "Location features", "Outdoor", "Parking and facilities", "Services", "Not included","All amenities"]. Otherwise, the app will crash. Use "All amenities" to get all the amenities.',
                    }
                    

                },
                "required": ['amenity']
            }
            }      
] 


class llm:

    def __init__(self):
        self.responseType = "text"
        self.imgs = []
        self.random_imgs = []
        self.function_descriptions = function_descriptions
        self.instruction = "you are help full assistant. you assist our customers by answering questions about our property we have on airbnb. you only assist users with only our property and business realted question. if the user prompt is not related to our service and business. eg. 'how to be good sells man?','how is a car made','how to cook a pizza' dont assist! tell them to google it or somthing. '"

    def get_base64_encoded_image(self,image_url):
        # Send a GET request to fetch the image at the URL
        response = requests.get(image_url)
        
        # Ensure the request was successful
        if response.status_code == 200:
            # Encode the binary content of the image
            encoded_image = base64.b64encode(response.content)
            # Decode the bytes to a string
            return encoded_image.decode('utf-8')
        else:
            return "Failed to fetch image"

    def image_randomizer(self,imgs):
    
        def pick_random_numbers(list_of_numbers, number_of_numbers_to_pick):
            random_numbers = []
            picked_numbers = set()
            for _ in range(number_of_numbers_to_pick):
              while True:
                random_number = random.randint(0, len(list_of_numbers) - 1)
                if random_number not in picked_numbers:
                  break
              picked_numbers.add(random_number)
              random_numbers.append(list_of_numbers[random_number])
            return random_numbers
        
        sequence = []
        n = len(imgs)
        for i in range(n):
          sequence.append(i)

        list_of_numbers = sequence
        number_of_numbers_to_pick = 1
        random_numbers = pick_random_numbers(list_of_numbers, number_of_numbers_to_pick)
        return random_numbers
    def function_call(self,response,_id):
        
        function_call = response["candidates"][0]["content"]["parts"][0]["functionCall"]
        function_name = function_call["name"]
        function_args = function_call["args"]
        print(type(function_args))
        with open("properties.json", "r") as f:
                properties = json.load(f)
    
        if function_name == "save_user_information":
            info = {}
            try:
                name = function_args["name"]
            except:
                info["personalName"] = ""
            try:
                email = function_args["email"]
            except:
                info["email"] = ""
            
            return {"function_response":database.set_user_info(_id,info),"image":None}
    
        if function_name == "get_property_info":
            arg = function_args["information_needed"]
            if arg == "price":

                price = airbnb.get(query="price")
                return {"function_response": f'The price for a day is €{price}',"image":None}
                
            if arg == "availability":

                availability = airbnb.get(query="availability")
                return {"function_response":f'1 = available\ndate = {today}\n{availability}',"image":None}

            try:
                return {"function_response": properties["642919"][arg],"image":None}
                
            except:
                pass

            return {"function_response": 'Error: the information is in the description.',"image":None}
               

        if function_name == "get_aminities_info": 
            try:
                aminities = function_args['aminities']
            except:
                aminities = "All amenities"
            if aminities == "All amenities":
                return {"function_response":str(properties['642919']['amenities']),"image":None}
                
            else:
                try:
                    return {"function_response":str(properties['642919']['amenities'][aminities]),"image":None}
                    
                except:
                    return {"function_response":'Error: amenity not found.',"image":None}
                    

        if function_name == "off_topic":
            return {"function_response":'you should only assist the user with only our property and business realted question.so dont assist! tell them to google it or somthing.',"image":None}

        if function_name == "include_image":
            arg = function_args["image_of"]
            self.responseType = 'image'

            try:
                self.imgs = properties["642919"]['images'][arg]
                self.random_imgs = self.image_randomizer(self.imgs)
                image = self.imgs[self.random_imgs[0]]
                print("image",image)
                encoded_image = self.get_base64_encoded_image(image)
                if encoded_image == "Failed to fetch image":
                    encoded_image = None
                return {"function_response":f'image of {arg} will be sent with your reponses.dont say "I am currently unable to send images." so pretend like you sent the image.',"image":encoded_image}

            except Exception as e:
                print(f"An error occurred: {str(e)}")
                traceback.print_exc()
                self.responseType = 'text'
                return {"function_response":'image not found with this argument please use one of them [outdoor, house, bedroom, bathroom]. If it doesn\'t match you can just pass.',"image":None}


    def generate_response(self,_id,messages,required_user_info,):
    
        data = {
                "contents": messages,
                "system_instruction": {
                      "parts": [
                        {
                          "text": self.instruction
                        }, 
                      ],
                      "role": "system" 
                    },
                "tools": [{
                    "functionDeclarations": self.function_descriptions
                    }],
                "safetySettings": [
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
        ],
                "generationConfig": {
                "temperature": 0.1,
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 2048,
                "stopSequences": [],
                #'safety_settings': [{"category":"HARM_CATEGORY_DEROGATORY","threshold":4},{"category":"HARM_CATEGORY_TOXICITY","threshold":4},{"category":"HARM_CATEGORY_VIOLENCE","threshold":4},{"category":"HARM_CATEGORY_SEXUAL","threshold":4},{"category":"HARM_CATEGORY_MEDICAL","threshold":4},{"category":"HARM_CATEGORY_DANGEROUS","threshold":4}]
              },}

        print("generating answer ... ")
        while True:
            try:
                print("Executing request...")
                response = requests.post(url, headers=headers, json=data)
                print(f"Status Code: {response.status_code}, Response Body: {response.text}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data:
                        print("Valid response received:", response_data)
                        break
                    else:
                        print("Empty JSON response received, retrying...")
                else:
                    print(f"Received non-200 status code: {response.status_code}")
                
                time.sleep(5)
            except requests.exceptions.RequestException as e:
                print(f'Request failed: {e}, retrying...')
                time.sleep(5)
        
        while "functionCall" in response_data["candidates"][0]["content"]["parts"][0]:
            
            function_call = response_data["candidates"][0]["content"]["parts"][0]["functionCall"]
            function_name = function_call["name"]

            function_response = self.function_call(response_data,_id)
            function_response_message = function_response["function_response"]
            function_response_image = function_response["image"]
            
            #bot.send_chat_action(tg.chat.id, 'typing')

            result = json.dumps(function_response)
            function = [{
                        "functionCall": {
                        "name": function_name,
                        "args": function_call["args"]
                                        }             
                            }]
            functionResponse = [{
                                "functionResponse":{
                                    "name": function_name,
                                    "response":{
                                        "name": function_name,
                                        "content": function_response_message
                                                }
                                                    }  
                                    },
                                    
                                    ]
            if function_response_image != None:
                functionResponse.append({"text": "here is the image sent to the user describe it well."},)
                functionResponse.append({
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": function_response_image,
                        }
                        }
                    )
            database.add_message(_id,function,"model")
            database.add_message(_id,functionResponse,"function")   
            messages.append({
                            "role": "model",
                            "parts": function
                            },)
            messages.append({"role": "function",
                            "parts": functionResponse
                                }) 
            while True:
                try:
                    print("Executing request...")
                    response = requests.post(url, headers=headers, json=data)
                    print(f"Status Code: {response.status_code}, Response Body: {response.text}")
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        if response_data:
                            print("Valid response received:", response_data)
                            break
                        else:
                            print("Empty JSON response received, retrying...")
                            ask_response = {"role": "user",
                                            "parts": [{"text": "??"}]
                                            }
                            if messages[-1] != ask_response:
                                messages.append(ask_response)
                                print(messages[-1])
                    else:
                        print(f"Received non-200 status code: {response.status_code}")
                    
                    time.sleep(5)
                except requests.exceptions.RequestException as e:
                    print(f'Request failed: {e}, retrying...')
                    time.sleep(5)
            

        return response_data["candidates"][0]["content"]["parts"][0]["text"]
