from pymongo import MongoClient
import os
from dotenv import load_dotenv


load_dotenv()

client = MongoClient(os.environ.get("MongoConnection"))
db = client['AirbnbAssistant']
Users = db['GOOGLE']
property = db['PropertyData']
instruction = "you are help full assistant. you assist our customers by answering questions about our property we have on airbnb. you only assist users with only our property and business realted question."

def reset_conversation(_id):
    Users.update_one({"_id":int(_id)},{"$set":{"conversation":[]}})

def register(_id,first_name,username): 
    existance = Users.find_one({"_id":int(_id)})
    if existance == None:
        Users.insert_one({"_id":_id,"firstName":first_name,"userName":username,"email":"","personalName":"","conversation":[]})
    
def add_message(_id,message,role):
    conversation = Users.find_one({"_id":_id}).get("conversation")
    conversation.append({"role":role,"parts":message})
    Users.update_one({"_id":int(_id)},{"$set":{"conversation":conversation}})
    return conversation
  
def required_user_info(_id): 
    # returns user Email and Name
    required_info = {}
    email = Users.find_one({"_id":_id}).get("email")
    personalName = Users.find_one({"_id":_id}).get("personalName")
    user_info = {"email":email,"personalName":personalName}
    required_info = [field for field in ["email", "personalName"] if user_info[field] == ""]
    return required_info

def set_user_info(_id:int,info):
    Users.update_one({"_id":int(_id)},{"$set":info})

def get_scraped_data(_id:int):
    return property.find_one({"_id":_id})

def save_property_info(_id:int,key:str,value):
    property.update_one({"_id":_id,},{"$set":{key:value}},upsert=True)

def set_current_property(_id:int,room_id:int):
    Users.update_one({"_id":_id},{"$set":{"current_property":room_id}},upsert=True)

def get_current_property(_id:int):
    return Users.find_one({"_id": _id}).get("current_property", None)
