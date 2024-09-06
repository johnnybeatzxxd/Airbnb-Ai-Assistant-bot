import google.generativeai as genai
import base64
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ.get("GeminiProKey1")
if api_key is None:
    api_key = os.environ.get("GeminiProKey")


def image_to_base64(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode('utf-8')
    else:
        return None



def analyze_images(images):

    genai.configure(api_key=api_key)
    conversations = []
    for image in images:
        conversations.append({
      "role": "user",
      "parts":[
          {
            "text": "Id: {}".format(image["id"])
          },
        {
          "inline_data": {
            "mime_type":"image/jpeg",
            "data": image_to_base64(image["image_url"])
          }
        }
      ]
    },)

    # Create the model
    generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
     "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-exp-0827",
    generation_config=generation_config,
    system_instruction="your are a helpful image analyzer!",
    )

    chat_session = model.start_chat(
        history=conversations,
        enable_automatic_function_calling=False,
    )
    response = chat_session.send_message("""
        I want you to see all the images carefuly and create a JSON where the key is the image type and the value is an array of the image id. empty array is not allowed!
        Example: "images":{
      "bedroom":[ids],
      "outdoor":[ids],
      "bathroom":[ids],
      "kitchen":[ids],
    }""",)

    parts = json.loads(response.text)
    return parts["images"]

