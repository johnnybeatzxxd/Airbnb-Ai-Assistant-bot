from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from . import database
from . import ai
from .createPropInfo.setup import *
import telebot
import datetime
import os
import time
import base64
import io
import markdown
from dotenv import load_dotenv
import re
import gobnb

load_dotenv()

bot = telebot.TeleBot(os.environ.get("TelegramBotToken"))



def remove_unsupported_tags(html_string):

  supported_tags = ["b", "strong", "i", "em", "a", "code", "pre"]
  
  pattern = r"<[^>]+>" 
  
  def replace_tag(match):
    tag = match.group(0)
    
    if any(tag.startswith(f"<{supported_tag}") or tag.startswith(f"</{supported_tag}") for supported_tag in supported_tags):
      return tag  
    else:
      return ""  
  
  clean_string = re.sub(pattern, replace_tag, html_string)
  return clean_string

# Create your views here.
def markups():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)   
    reset = telebot.types.KeyboardButton('💁‍♂ Reset')   
    delete_property = telebot.types.KeyboardButton("❌Delete Property")
    markup.add(reset)
    markup.add(delete_property)
    return markup
class TelegramWebhookView(View):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    @bot.message_handler(content_types=['text', 'photo'])
    def chat(customer):
    
        if customer.content_type == "photo":
            current_property = database.get_current_property(id_)
            if current_property == None:
                return
            caption = customer.caption
            bot.send_chat_action(customer.chat.id, 'typing')
            prompt = []
            photo = customer.photo[-1]
            raw = photo.file_id  # Get the file_id of the photo
            file_info = bot.get_file(raw)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Use BytesIO to handle the image data in memory
            image_stream = io.BytesIO(downloaded_file)
            image_data = base64.b64encode(image_stream.getvalue()).decode('utf-8')
            
            if caption != None:
                prompt.append({"text": caption},)
            prompt.append({
                "inlineData": {
                    "mimeType": "image/png",
                    "data": image_data
                }
            })
        if customer.content_type == "text":
            prompt = [
                {"text": customer.text},  
            ]

        first_name = customer.from_user.first_name
        username = customer.from_user.username
        id_ = customer.chat.id
        current_property = database.get_current_property(id_)
        # reset the conversation
        if customer.content_type == "text" and prompt[0]["text"] == '💁‍♂ Reset':
            database.reset_conversation(id_)
        # delete the current property
        if customer.content_type == "text" and prompt[0]["text"] == "❌Delete Property":
            # if user has current property
            if current_property:
                database.delete_property_data(current_property)
                bot.send_message(id_,"Your property has been deleted!\nplease provide a new property link or roomd id.")
                return
        else:
            database.register(id_,first_name,username)
            # check if user has current property
            if current_property is None:
                room_id = get_room_id(customer.text)
                if room_id is None:
                    bot.send_message(id_, "please provide which property you looking for!\naribnb link / room id.", reply_markup=markups(), parse_mode='HTML')
                    return None
                else:
                   
                    bot.send_message(id_, "Thank you for providing your property. I am currently working on it and will inform you once I have finished.")
                    # generate needed information using the given room id
                    if generate_property_data(room_id):
                        database.set_current_property(id_,room_id)
                        bot.send_message(id_,"Dear user your property is ready you can now ask me about anything about your property")
                        database.reset_conversation(id_)

            conversation = database.add_message(id_,prompt,"user")
            required_user_info = database.required_user_info(id_)

            llm = ai.llm(id_)
            if llm is None:
                # the property data has a problem it should be deleted and recreated!
                bot.send_message(id_,"Your current property is corrupted!\nyou should delete the current property data and provide your current property link to fix it.")
                # maybe give a few options to delete the corrupted property data.. i will impliment it later.
                return 
            response = llm.generate_response(id_,conversation,required_user_info)
            escaped_response = markdown.markdown(response)
            #print(response)
            response = [
                {"text": response},  
            ] 
            database.add_message(id_,response,"model")
            if llm.responseType == 'image':
                images = [llm.imgs[i] for i in llm.random_imgs]
                media_group = [telebot.types.InputMediaPhoto(image, escaped_response) for image in images]

                #bot.send_media_group(id_, media_group)
                escaped_response = remove_unsupported_tags(escaped_response)
                bot.send_photo(id_, images[0], caption=escaped_response, parse_mode='HTML')

            else:
                escaped_response = remove_unsupported_tags(escaped_response)
                bot.send_message(id_, escaped_response, reply_markup=markups(), parse_mode='HTML')


        

    def post(self, request):        
        bot.process_new_updates([telebot.types.Update.de_json(request.body.decode("utf-8"))])
        return HttpResponse("!", status=200)
