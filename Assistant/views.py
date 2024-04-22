from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from . import database
from . import ai
import telebot
import openai
import datetime
import os
import time
import base64
import io  # Import the io module
import markdown
from dotenv import load_dotenv
import re

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
    markup.add(reset)
    return markup
class TelegramWebhookView(View):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    @bot.message_handler(content_types=['text', 'photo'])
    def chat(customer):
        if customer.content_type == "photo":
            caption = customer.caption
            print(caption)
            bot.send_chat_action(customer.chat.id, 'typing')
            prompt = []
            photo = customer.photo[-1]
            raw = photo.file_id  # Get the file_id of the photo
            file_info = bot.get_file(raw)
            print(file_info)  # Get the File object
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
        
        if customer.content_type == "text" and prompt[0]["text"] == '💁‍♂ Reset':
            database.reset_conversation(id_)

        else:
            database.register(id_,first_name,username)
            conversation = database.add_message(id_,prompt,"user")
            required_user_info = database.required_user_info(id_)
            llm = ai.llm()
            response = llm.generate_response(id_,conversation,required_user_info)
            escaped_response = markdown.markdown(response)
            response = [
                {"text": escaped_response},  
            ] 
            database.add_message(id_,response,"model")
            images = []
            if llm.responseType == 'image':
                for i in llm.random_imgs:
                    images.append(llm.imgs[i])            
                media_group = []
                for image in images:
                    media_group.append(telebot.types.InputMediaPhoto(image,escaped_response))

                #bot.send_media_group(id_, media_group)
                escaped_response = remove_unsupported_tags(escaped_response)
                print(escaped_response)
                bot.send_photo(id_, images[0], caption=escaped_response, parse_mode='HTML')

            else:
                escaped_response = remove_unsupported_tags(escaped_response)
                print(escaped_response)
                bot.send_message(id_, escaped_response, reply_markup=markups(), parse_mode='HTML')


        

    def post(self, request):        
        bot.process_new_updates([telebot.types.Update.de_json(request.body.decode("utf-8"))])
        return HttpResponse("!", status=200)
