import requests
from serpapi import GoogleSearch
from dotenv import load_dotenv
import os

load_dotenv()

ser_api_key = os.getenv("SER_API_KEY")

def get_restaurants(lat, lng):
    ll = f"@{lat}, {lng},15.1z"
    params = {
    "engine": "google_maps",
    "q": "restaurants",
    "ll": ll,
    "type": "search",
    "api_key": ser_api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    local_results = results["local_results"]

    restaurants  = []
    for res in local_results:
        temp_array = [res['title'], res['website']]
        restaurants.append(temp_array)

    return restaurants

res = get_restaurants(40.7455096,-74.0083012)

print(res)