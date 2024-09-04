import requests
import datetime
import json


def get(query,room_id):
    
    today = datetime.date.today()
    year = today.year
    month = today.month
    day = today.day
    
    if query == 'price':
        
        url = "https://airbnb-listings.p.rapidapi.com/v2/listingPrices"
        
        querystring = {"id":f"{room_id}","year":f"{year}","month":f"{month}"}

        headers = {
        	"X-RapidAPI-Key": "7332d10eabmshe3583ada7bc70a2p13b937jsnb5bd2c435279",
        	"X-RapidAPI-Host": "airbnb-listings.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)


        response = response.json()
        day = int(day) - 1
        return response["results"][day]
    
    if query == "availability":
       

        url = "https://airbnb-listings.p.rapidapi.com/v2/listingavailability"

        querystring = {"id":f"{room_id}","year":f"{year}","month":f"{month}"}

        headers = {
        	"X-RapidAPI-Key": "7332d10eabmshe3583ada7bc70a2p13b937jsnb5bd2c435279",
        	"X-RapidAPI-Host": "airbnb-listings.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        return response.json()
    