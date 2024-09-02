import re
from .create_function_description import function_desc
from .pure_data_gen import generate_pure_data
from ..database import *

def get_room_id(url):
    try:
        if "airbnb.com/rooms" in url:
            match = re.search(r'/rooms/(\d+)', url)
            if match:
                room_id = match.group(1)
                print("Room ID:", room_id)
            else:
                raise ValueError("Room ID not found in the URL.")
        else:
            if url.isdigit():
                room_id = url
                print("Room ID:", room_id)
            else:
                raise ValueError("Not a valid Airbnb URL or room ID.")
    except Exception as e:
        print(f"Error: {e}")
        room_id = None
    return room_id



def generate_property_data(room_id:int):
        function_description = function_desc(room_id=int(room_id))
        function_description.create()
        generate_pure_data(room_id=int(room_id))
        return True



