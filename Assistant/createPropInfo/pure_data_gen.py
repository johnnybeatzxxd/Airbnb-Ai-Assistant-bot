import json
import pprint
import os
from ..database import *

def generate_pure_data(room_id):

    # get the data needed to build the function information
    data = get_scraped_data(room_id)["scraped_data"]
    images = get_scraped_data(room_id)["analyzed_images"]
    

    location_cordinates = data["coordinates"]
    description = str(data.get("description", "")) + str( data.get("sub_description", {}))

    title = data["sub_description"]["title"]
    rules = data["house_rules"]
    location_description = data["location_descriptions"]

    aminites_info = {}
    for amenity in data["amenities"]:
        aminites_info[amenity["title"]] = amenity["values"]

    information_keys = list(data.keys())
    room_id = data["room_id"]


    new_data = {f"{room_id}":{
        "title":title,
        "description":description,
        "location":location_description,
        "location_cordinates":location_cordinates,
        "rules":rules,
        "aminities":aminites_info,
        "images":images,
    }}

    save_property_info(int(room_id),"function_information",new_data)
