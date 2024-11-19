import requests
from serpapi import GoogleSearch
from dotenv import load_dotenv
import os

load_dotenv()

ser_api_key = os.getenv("SER_API_KEY")

def get_freebase_id(city_name):
    url = f"https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbgetentities",
        "titles": city_name,
        "sites": "enwiki",
        "format": "json"
    }
    response = requests.get(url, params=params)
    data = response.json()
    entities = data.get('entities', {})
    
    for entity in entities.values():
        claims = entity.get('claims', {})
        if 'P646' in claims:  # P646 is the Freebase ID property
            return claims['P646'][0]['mainsnak']['datavalue']['value']
    return None


def get_flight_price(departure_id, arrival_id, outbound_date, return_date=None, 
                currency="USD", language="en", country="us", travel_type=1, 
                adults=1, children=0):

    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "return_date": return_date if travel_type == 1 else None,
        "currency": currency,
        "hl": language,
        "gl": country,
        "type": travel_type,
        "adults": adults,
        "children": children,
        "api_key": ser_api_key
    }

    try:
        # Search for flights using the API
        search = GoogleSearch(params)
        results = search.get_dict()

        # Extracting relevant details
        flights = []
        if "best_flights" in results:
            for flight in results["best_flights"]:
                price = flight.get("price", "N/A")
                airlines = [leg["airline"] for leg in flight.get("flights", [])]
                flights.append({"price": price, "airlines": airlines})
        
        if flights:
            flight = flights[0]
            return flight["airlines"][0], flight["price"]
        else:
            return "No flights found", 0
    except Exception as e:
        print(f"Error fetching flights: {e}")
        return "Error", 0


# Example usage
london_id = get_freebase_id("london")
paris_id = get_freebase_id("paris")
print(f"London Freebase ID: {london_id}")
print(f"Paris Freebase ID: {paris_id}")
outbound = "2024-11-25"
return_date = "2024-11-27"
flight, price = get_flight_price(london_id, paris_id, outbound, return_date)
print(flight, price)



