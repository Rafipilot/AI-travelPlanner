from serpapi import GoogleSearch
from dotenv import load_dotenv
import os

load_dotenv()
ser_api_key = os.getenv("SER_API_KEY")

def get_restaurants(lat, lng):
    ll = f"@{lat}, {lng},15.1z"
    params = {
    "engine": "google_maps",
    "q": "pizza",
    "ll": ll,
    "type": "search",
    "api_key": ser_api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    local_results = results["local_results"]

    restaurants  = []
    for res in local_results:
        print(res["title"])
        res.append(res["title"])

    return restaurants

