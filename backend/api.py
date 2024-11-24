from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from bs4 import BeautifulSoup
from amadeus import Client, ResponseError
from openai import OpenAI
import requests
import pandas as pd
from serpapi import GoogleSearch
import re 
import random 
from dotenv import load_dotenv
import os

load_dotenv()

am_key = os.getenv("AM_KEY")
am_auth = os.getenv("AM_AUTH")
google_api_key = os.getenv("GOOGLE_API_KEY")
ser_api_key = os.getenv("SER_API_KEY")
openai_key = os.getenv("OPENAI_KEY")




app = Flask(__name__)
CORS(app, supports_credentials=True)

client = OpenAI(api_key=openai_key)
# Load the CSV file directly from the URL For getting airline name from code
url_airline_codes = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat" #Data set for code to name
df_ac = pd.read_csv(url_airline_codes, header=None, names=["AirlineID", "Name", "Alias", "IATA", "ICAO", "Callsign", "Country", "Active"])


# Replace \N with NaN for missing values
df_ac.replace(r'\\N', pd.NA, inplace=True, regex=True)

# Filter out rows without IATA codes
df = df_ac[df_ac['IATA'].notna()]

# Create a dictionary of IATA codes to airline names
airline_codes = dict(zip(df['IATA'], df['Name']))

# Initialize Amadeus client
amadeus = Client(
    client_id=am_key,
    client_secret=am_auth
)

def get_freebase_id(city_name):
    # Ensure the city name is properly capitalized (first letter uppercase)
    city_name = city_name.strip().title()
    city_aliases = {
    "New York": "New York City",
    "Washington": "Washington, D.C."
}
    if city_name in city_aliases:
        city_name = city_aliases[city_name]
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


def get_coords(city_name):
    geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={google_api_key}'
    geocode_response = requests.get(geocode_url)


    if geocode_response.status_code == 200:
        geocode_data = geocode_response.json()
        if geocode_data['status'] == 'OK' and geocode_data['results']:
            # Get latitude and longitude
            lat = geocode_data['results'][0]['geometry']['location']['lat']
            lng = geocode_data['results'][0]['geometry']['location']['lng']
        return lat, lng
    else:
        print("Error with google api")

def get_website(name):  
    url = 'https://www.google.com/search'
    headers = {
        'Accept' : '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82',
    }

    parameters = {'q': name}
    content = requests.get(url, headers = headers, params = parameters).text
    soup = BeautifulSoup(content, 'html.parser')
    search = soup.find(id = 'search')
    first_link = search.find('a')
    return first_link['href']

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
        restaurants .append(res["title"])

    return restaurants

def get_activities(city_name, lat ,lng):


    #Use the Places API to get nearby activities (tourist attractions)
    places_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    places_params = {
        'location': f'{lat},{lng}',  # Lat, Lng coordinates
        'radius': 5000,  # Search within a 5 km radius 
        'type': 'tourist_attraction',  # Type of places to search for
        'key': google_api_key  
    }

    # Make the request to the Places API
    places_response = requests.get(places_url, params=places_params)

    if places_response.status_code == 200:
        places_data = places_response.json()

        # Check if there are any results
        if places_data['results']:
            activities = []
            for place in places_data['results']:
                name = place.get('name')
                address = place.get('vicinity')
                place_id = place.get('place_id')


                details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
                details_params = {
                    'place_id': place_id,
                    'key': google_api_key
                }

                # Make the request to the Place Details API
                details_response = requests.get(details_url, params=details_params)
                if details_response.status_code == 200:
                    details_data = details_response.json()
                    if details_data['status'] == 'OK':
                        # Get the description from the Place Details API response
                        description = details_data['result'].get('editorial_summary', {}).get('overview', 'No description available')
                    else:
                        description = 'No description available'
                else:
                    description = 'Error retrieving details'

                # Append the activity details to the list
                activities.append([name, address, description])

            return activities
        else:
            print("No activities found near the city.")
    else:
        print("Error retrieving places:", places_response.status_code, places_response.text)



def get_average_temp(location, depart_date):
    # Convert depart_date from string to datetime if it's a string
    if isinstance(depart_date, str):
        try:
            depart_date = datetime.strptime(depart_date, "%Y-%m-%d")  # Adjust the format as needed
        except ValueError:
            return "Error: depart_date format is incorrect. Expected format: YYYY-MM-DD."

    # Extract the month from the depart_date
    location = location.lower()
    month = depart_date.strftime("%B").lower()

    # Format the URL to match the location and month
    url = f"https://www.holiday-weather.com/{location}/averages/{month}/"
    
    # Send a request to the URL
    response = requests.get(url)
    if response.status_code != 200:
        print("Error accessing weather information")
        return f"Error: Unable to access page for {location} in {month}."

    # Parse the page content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the div containing the average temperature
    temp_div = soup.find("div", class_="p-2 pl-md-3 text fw-600")
    if temp_div:
        # Extract the temperature text
        temp = temp_div.text.strip()
        return f"The average temperature in {location} during {month} is {temp}."
    else:
        return f"Could not find temperature information for {location} in {month}."



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
                url = get_website(airlines)
                flights.append({"price": price, "airlines": airlines, "url":url})
        
        if flights:
            return flights

        else:
            return "No flights found", 0
    except Exception as e:
        print(f"Error fetching flights: {e}")
        return "Error", 0


def get_hotel_data(city_name, lat, lng, checkin, checkout, number_people):
    try:
        # Define parameters for the request
        params = {
            'engine': 'google_hotels',
            'q': f"Hotels in {city_name}",
            'check_in_date': checkin,
            'check_out_date': checkout,
            'api_key': ser_api_key,
            'adults': number_people,
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Check if there are results in the response
        hotels = []
        if 'properties' in results:
            for property in results['properties']:
                price_string = property.get('rate_per_night', {}).get('lowest', 'Price not available')
                # Remove non-numeric characters (like '$', commas, etc.)
                price_clean = re.sub(r'[^\d.]', '', price_string)
                
                # Convert to float, if it's valid
                try:
                    price = float(price_clean)
                except ValueError:
                    price = None  # In case conversion fails
                
                hotel_data = {
                    'name': property.get('name'),
                    'price': price if price is not None else 0,
                    'url': property.get('link', 'No URL available'),
                    "coords": property.get('gps_coordinates')
                }
                hotels.append(hotel_data)
            
            if len(hotels) != 0:
                return hotels
            else:
                print(hotels)
                print("No hotels found with serapi")
    except Exception as e:
        print("Error with serapi", e)


    
    except Exception as e:
        print("error occured", e)
        return []

def get_openai_response(number_of_people, departure, destination, duration,flights, weather_info, best_hotels, activities, restaurants, cost, budget, per_person_cost):
    prompt = (
    f"You are an expert travel planner. Based on the details provided below, create a structured, "
    f"personalized, and informative travel plan. The plan should be balanced, staying within the given "
    f"budget and trip duration. Please follow the guidelines for each section:\n\n"

    f"Travel plan for departure to destination city"

    f"**Trip Overview:**\n"
    f"- Trip Duration: {duration} days\n"
    f"- Number of Travelers: {number_of_people}\n"
    f"- Departure Location: {departure}\n"
    f"- Destination Location: {destination}\n\n"
    f"- Budget: {budget}"

    f"**Flight Information:**\n"
    f"Info: {flights} "
    f"- Airline: {flights["airlines"][0]}\n"
    f"- Price: {flights["price"]}$ (Return tickets)\n"
    f"- Flight Details: Departure from {departure} and return from {destination}. Include flight duration and any relevant details.\n\n"
    f"- URL to bookling page of airline: {flights["url"]}"

    f"**Weather info**"
    f"{weather_info}"
    f"Based on weather info give some tips to the traveller(s)"

    f"**Hotel Recommendation**\n"
    f"{best_hotels}"
    f"- Price (Per night):"
    f"- CLick here to book your stay at"

    f"**Restaurant Options based on your hotel location:"
    f"{restaurants}"

    f"**Activities and Attractions:**\n"
    f"- Based on the duration of the trip, suggest activities that are relevant to the destination. Maybe like 1-2 activites per day "
    f"actvities list: {activities}\n"
    f"- Include brief descriptions of each activity and links to booking or more details if available.\n\n"

    f"**Day-by-Day Itinerary:**\n"
    f"- Create a detailed day-by-day itinerary based on the trip duration. Include suggested times for activities listed above, when yuou recommend restaurants, pick from the given ones. "
    f"transportation tips, and meal recommendations.\n"
    f"Include the days that the Traveller(s) arrive"
    f"- Balance the itinerary to avoid overwhelming the traveler, but also ensure that the trip is fulfilling and diverse.\n\n"

    f"**Budget Breakdown:**\n"
    f"- Flights (depends on airline chosen): {flights['price']}\n\n"
    f"- Hotels: {best_hotels[1]*int(duration)}\n\n" #fix budget
    f"- Meals and activities: {per_person_cost}\n\n"
    f"- Total: {cost}\n\n"

    f"**Additional Tips:**\n"
    f"- Provide useful travel tips, such as advice on local customs, transportation options (e.g., metro, taxis), and "
    f"any cultural insights specific to {destination}.\n\n"

    f"Ensure that the plan is practical, engaging, and inspiring. The tone should be exciting and easy to follow, "
    f"with clear steps for the traveler to enjoy their journey."
)
    try:
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=1200,
        temperature=0.7,
        )
        travel_plan = response.choices[0].message.content
        return travel_plan
    except Exception as e:
        print("Api error with openai : ", e)
        return "Error with Openai Gpt-3"

#route definitions
@app.route('/api/travel', methods=['POST'])
def travel_agent():
    data = request.get_json()
    departure = data.get('departure_city')
    destination = data.get('destination_city')
    number_of_people = data.get('number_of_people')
    budget = data.get('budget_range')
    depart_date = data.get('departure_date')
    return_date = data.get('return_date')

    print(departure, destination)

    d1 = datetime.strptime(str(depart_date), "%Y-%m-%d")
    d2 = datetime.strptime(str(return_date), "%Y-%m-%d")
    duration = (d2 - d1).days


    print(depart_date, return_date)
    lat, lng = get_coords(destination)
    activities = get_activities(destination, lat, lng)
    random.shuffle(activities)
    activities_to_return = []
    for i in range(duration):
        activities_to_return.append(activities[i])

    Cost = int(0)
    # Calculate duration and validate dates

    weather_info = get_average_temp(destination, depart_date)

    
    hotels = get_hotel_data(destination, lat, lng, str(depart_date), str(return_date),number_people=number_of_people )

    departure_id = get_freebase_id(departure)
    destination_id = get_freebase_id(destination)
    
    flights = get_flight_price(departure_id, destination_id, str(depart_date), str(return_date), adults=number_of_people)

    flights_prices = []
    for flight in flights:
        flights_prices.append(flight["price"])
    average_price = sum(flights_prices)/len(flights_prices)
    print(average_price)

    Cost = Cost + average_price
    hotel_info = ""
    per_night_budget = (int(budget - int(average_price))) - 100 * duration
    # Initialize variables
    
    best_hotels = []
    min_price_diffs = []

    # Find the four hotels with prices closest to the budget
    for hotel in hotels:
        hotel_info += f"- **{hotel['name']}**\n"
        hotel_info += f"  - Price: {hotel['price'] * (duration - 1)}\n"
        hotel_info += f"  - [Click here to book]({hotel['url']})\n"

        price = int(float(hotel['price']))
        price_diff = abs(per_night_budget - price)
        
        # Add each hotel to the list with its price difference
        min_price_diffs.append((hotel, price_diff))

        # Sort by price difference and select the top 4
        min_price_diffs = sorted(min_price_diffs, key=lambda x: x[1])[:4]
        best_hotels = [[hotel['name'], hotel['price'], hotel['url']] for hotel, diff in min_price_diffs]

    openai_response = get_openai_response(budget, depart_date, return_date, number_of_people, departure, destination, duration, flights=flights, flight_price=average_price, weather_info=weather_info, best_hotels=best_hotels, activities=activities, Cost=Cost, city_destination=destination)

    response = {
        "status": "success",
        "message": "Travel details received",
        "details": {
            "openai_response": openai_response,
            "flights": flights,
            "best_hotels": best_hotels,
            "activities": activities_to_return,
        }
    }
    return jsonify(response)

@app.route('/api/first_step', methods=['POST'])
def flights_and_hotels():
    data = request.get_json()
    departure = data.get('departure_city')
    destination = data.get('destination_city')
    number_of_people = data.get('number_of_people')
    budget = data.get('budget_range')
    depart_date = data.get('departure_date')
    return_date = data.get('return_date')
    
    d1 = datetime.strptime(str(depart_date), "%Y-%m-%d")
    d2 = datetime.strptime(str(return_date), "%Y-%m-%d")
    duration = (d2 - d1).days



    lat, lng = get_coords(destination)

    Cost = int(0)
    
    hotels = get_hotel_data(destination, lat, lng, str(depart_date), str(return_date),number_people=number_of_people )

    departure_id = get_freebase_id(departure)
    destination_id = get_freebase_id(destination)

    flights = get_flight_price(departure_id, destination_id, str(depart_date), str(return_date), adults=number_of_people)
    try:
        flights_prices = []
        for flight in flights:
            flights_prices.append(flight["price"])
        average_price = sum(flights_prices)/len(flights_prices)
    except Exception as e:
        print("Could not find any flight options", e)
        average_price = 0
    print(average_price)

    Cost = Cost + average_price
    hotel_info = ""
    per_night_budget = (int(budget - int(average_price))) - 100 * duration
    # Initialize variables
    
    best_hotels = []
    min_price_diffs = []

    # Find the four hotels with prices closest to the budget
    for hotel in hotels:
        hotel_info += f"- **{hotel['name']}**\n"
        hotel_info += f"  - Price: {hotel['price'] * (duration - 1)}\n"
        hotel_info += f"  - [Click here to book]({hotel['url']})\n"

        price = int(float(hotel['price']))
        price_diff = abs(per_night_budget - price)
        
        # Add each hotel to the list with its price difference
        min_price_diffs.append((hotel, price_diff))

        # Sort by price difference and select the top 4
        min_price_diffs = sorted(min_price_diffs, key=lambda x: x[1])[:4]
        best_hotels = [[hotel['name'], hotel['price'], hotel['url'], hotel['coords']] for hotel, diff in min_price_diffs]

        response = {
        "status": "success",
        "message": "Travel details received",
        "details": {
            "flights": flights,
            "best_hotels": best_hotels,
        }
    }
    return jsonify(response)

@app.route('/api/second_step', methods=['POST'])
def response():
    data = request.get_json()
    flights = data.get('selectedFlight')
    hotels = data.get('selectedHotel')
    departure = data.get('departure_city')
    destination = data.get('destination_city')
    number_of_people = data.get('number_of_people')
    depart_date = data.get('departure_date')
    return_date = data.get('return_date')
    budget = data.get('budget')


    weather = get_average_temp(destination, depart_date)
    lat= hotels[3]['latitude']
    lng = hotels[3] ['longitude']


    res = get_restaurants(lat, lng)
    activities = get_activities(destination, lat, lng)


    d1 = datetime.strptime(str(depart_date), "%Y-%m-%d")
    d2 = datetime.strptime(str(return_date), "%Y-%m-%d")
    duration = (d2 - d1).days

    cost = 0  
    per_person_cost = int(number_of_people)*50*int(duration)
    print(number_of_people, duration)
    print("per person",per_person_cost)
    cost = cost + int(hotels[1]*int(duration)) + int(flights['price']) + int(per_person_cost)

    ai_response = get_openai_response(number_of_people=number_of_people, departure=departure, destination=destination, duration=duration, flights=flights, weather_info=weather, best_hotels=hotels, activities=activities, restaurants=res, cost=cost, budget=budget, per_person_cost=per_person_cost)
    
    response = {
        "status": "success",
        "message": "response",
        "details": {
            "response": ai_response,
        }
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
