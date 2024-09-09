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
    print(images)
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
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="You are a meticulous and detail-oriented image analyzer!", 
    )

    chat_session = model.start_chat(
        history=conversations,
        enable_automatic_function_calling=False,
    )
    response = chat_session.send_message("""
        ## Detailed Image Analysis Instructions:

        I have a list of images that I need you to carefully analyze and classify. Your task is to create a JSON object that accurately reflects the content of each image. 

        **JSON Structure:**

        The JSON object should have a single key called "images". The value of this key should be another object containing key-value pairs.

        * **Keys:** Represent the dominant type or category with three word of the image (e.g., "bedroom_double_bed", "outdoor_parking_lot", "bathroom_washing_sink", "kitchen_cooking_cabinate" etc.). Be specific and descriptive when choosing the category.
        * **Values:** Each key should have a value that is an array of image IDs. These IDs uniquely identify each image that belongs to that specific category. 

        **Example:**

        ```json
        {
          "images": {
            "bedroom": [ids],
            "outdoor": [ids],
            "bathroom": [ids],
            "kitchen": [ids]
          }
        }
        ```

        **Important Considerations:**

        * **Accuracy:**  Strive for the highest possible accuracy in classifying the images. 
        * **Dominant Category:** If an image contains elements of multiple categories, choose the category that is most prominent or dominant in the image. 
        * **Specificity:** Be as specific as possible when defining the image categories. For example, instead of just "outdoor", you could use "park", "beach", "forest", etc.
        * **No Empty Arrays:** Ensure that every category key has at least one image ID associated with it. Empty arrays are not allowed.
        * **Maximum Number of Keys:** The maximum number of unique category keys in the JSON object should be 20. If you encounter more than 20 distinct categories, try to group similar categories together or use a more general category to reduce the number of keys
        
        Please analyze the images thoroughly and create the JSON object according to these instructions. I appreciate your attention to detail! 
        """,)

    parts = json.loads(response.text)
    print(parts)
    return parts["images"]

