import json 
import re
import google.generativeai as genai
import base64
import requests
from .analyze_images import analyze_images
from Assistant.createPropInfo.pybnb.test import * 
from ..database import *

class function_desc:

    def __init__(self,room_id:int):
        self.image_keys = []
        self.aminities_key = []
        self.property_info_keys = ["title","description","price","availability","location_description","rules"]
        self.room_id = room_id
        

    def fetch_the_property_data(self,room_id:int):
        scraped_data = get_scraped_data(room_id)
        if  scraped_data == None:
            return test1(room_id)
        try:
            return scraped_data["scraped_data"]
        except:
            return test1(room_id) 

    def get_image_keys(self,data):
       
        image_urls = [{"id":index,"image_url":image["url"]} for index, image in enumerate(data["images"])]

        def update_dict(original_dict, update_dict):
            for key, values in update_dict.items():
                if key in original_dict:
                    original_dict[key].extend(values)
                else:
                    original_dict[key] = values
            return original_dict

        chunk_size = 10
        result = {}

        for i in range(0, len(image_urls), chunk_size):
            chunk = image_urls[i:i + chunk_size]
            chunk_result = analyze_images(chunk)
            result = update_dict(result, chunk_result)
            
        return result

    def create(self):
        # scrape the data from airbnb website
        data = self.fetch_the_property_data(room_id=self.room_id)
        print("Done fetching data.")
      

        # get aminities key
        print("fetching amenities key...")
        for key in data["amenities"]:
            self.aminities_key.append(key["title"])
        print("done fetching amenities key.")    
        
        
        # get images key 
        try:
            images_dict = get_scraped_data(self.room_id)["analyzed_images"]
        except:
            print("analyzing the images...")
            analyzed_images = self.get_image_keys(data)
            print("Analayzed image:",analyzed_images)
            self.image_keys = list(analyzed_images.keys())

            # save analyzed images for property data
            images_dict = {}
            for image_key in self.image_keys:
                image_indices = analyzed_images[image_key]
                image_urls = []
                for index in image_indices:
                    index = int(index)
                    image_urls.append(data["images"][index]["url"])

                images_dict[image_key] = image_urls

            # save analyzed images to the database
            save_property_info(self.room_id,"analyzed_images",images_dict)

        # create function description
        function_description = [
    {
        "name": "save_user_information",
        "description": "This function must be triggerd when customer provide their email and name. if the user provide one of them it should be saved instantly",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "save the name of the customer eg. anuar,yishak ..."
                },
                "email": {
                    "type": "string",
                    "description": "save the email of the customer eg. anuar@...,yishak@..."
                    }

            },
            "required": ["name","email"]
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
                    "description": "true or false"
                }

            },
            "required": ["off_topic"]
        }
        },
        
    {
        "name": "include_image",
        "description": "this function must be triggered when you always talk about specific area in our property. and when you want to show the area you are talking about.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_of": {
                    "type": "string",
                    "description": f"image to send with your responses. It must be one of the following: {self.image_keys}. Otherwise, say i dont have the image,choose one of them that matches with user question."
                }

            },
            "required": ["image_of"]
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
                    "description": f"The type of information requested. It must be one of the following: {self.property_info_keys}. Otherwise, the app will crash."
                }            

            },
            "required": ["information_needed"]
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
                    "description": f"The name of the amenity. It must be one of the following: {self.aminities_key}. Otherwise, the app will crash. Use 'All amenities' to get all the amenities."
                }
                

            },
            "required": ["aminities"]
        }
        }      
]
        
        # save function description
        save_property_info(self.room_id,"function_description",function_description)
        return function_description
