from serpapi import GoogleSearch
import os
from dotenv import load_dotenv

load_dotenv()
ser_api_key = os.getenv("SER_API_KEY")

def get_flights(departure_id, arrival_id, outbound_date, return_date=None, 
                currency="USD", language="en", country="us", travel_type=1, #travel type is round trip or not
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

    search = GoogleSearch(params)
    results = search.get_dict()

    # Extracting relevant details
    flights = []
    if "best_flights" in results:
        for flight in results["best_flights"]:
            price = flight.get("price", "N/A")
            airlines = [leg["airline"] for leg in flight["flights"]]
            flights.append({"price": price, "airlines": airlines})

    flight = flights[0]
    return flight["airlines"][0], flight["price"]

# Example usage
if __name__ == "__main__":
    departure = "LHR"  # London Heathrow
    arrival = "ATH"    # Athens
    outbound = "2024-11-19"
    return_date = "2024-11-25"

    # Replace 'your_serpapi_key' with your actual API key

    
    flight_name, flight_price= get_flights(departure, arrival, outbound, return_date)
    print(flight_name, flight_price)
