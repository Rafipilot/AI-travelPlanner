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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown2
from firebase_admin import credentials, auth
import firebase_admin
from firebase_admin import firestore




# Initialize Firebase Admin SDK
cred = credentials.Certificate("backend\\secrets\\travex-76b7c-firebase-adminsdk-e5972-d297b4d236.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
CORS(app)


load_dotenv()

am_key = os.getenv("AM_KEY")
am_auth = os.getenv("AM_AUTH")
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

def preprocess_markdown(content):   #processes gpt output to prepare for email
    # Add double spaces at the end of bullet points for proper line breaks
    lines = content.splitlines()
    processed_lines = []
    for line in lines:
        if line.strip().startswith(("-", "*")):  # Bullet points
            processed_lines.append(line + "  ")  # Add double space for line break
        else:
            processed_lines.append(line)
    return "\n".join(processed_lines)

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
    if search is not None:
        first_link = search.find('a')
        try:
            return first_link['href']
        except Exception as e:
            first_link = None
            return  "none found"
    else:
        first_link = None
        return "none found"

def get_restaurants(city, lat, lng):
    ll = f"@{lat}, {lng},15.1z"
    params = {
    "engine": "google_maps",
    "q": f"restaurants in {city}",
    "ll": ll,
    "type": "search",
    "api_key": ser_api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    local_results = results["local_results"]

    restaurants  = []
    for res in local_results:
        temp_array = [res.get('title', 'No Title'), res.get('website', 'No Website'), res.get('gps_coordinates')]
        restaurants.append(temp_array)

    return restaurants

def get_activities(city_name, lat ,lng):
    ll = f"@{lat}, {lng},15.1z"
    params = {
    "engine": "google_maps",
    "q": f"tourist attractions in {city_name}",
    "ll": ll,
    "type": "search",
    "api_key": ser_api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    local_results = results["local_results"]

    activities = []
    for act in local_results:
        temp_array = [act.get('title', 'No Title'), act.get('website', 'No Website'), act.get('gps_coordinates')]
        activities.append(temp_array)

    return activities



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


def get_hotel_data(city_name, checkin, checkout, number_people):
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
                    "coords": property.get('gps_coordinates'),
                    "picture": property.get('images')[0].get('original_image'),
                    "rating": property.get('overall_rating', 'Not available'),
                    "location_rating": property.get('overall_rating', 'Not available'),
                    "amenities": property.get('amenities', 'Not available'),
                    "description": property.get('description', 'Not available'),
                }
                hotels.append(hotel_data)
            
            if len(hotels) != 0:
                print("hotels: ", hotels)
                print(hotels)
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
    f"It is vital that your put links where shown for flight, hotel restaurant and activity info."

    f"Travel plan for departure to destination city"

    f"**Trip Overview:**\n"
    f"- Trip Duration: {duration} days\n"
    f"- Number of Travelers: {number_of_people}\n"
    f"- Departure Location: {departure}\n"
    f"- Destination Location: {destination}\n\n"
    f"- Budget: {budget}"

    f"**Day-by-Day Itinerary:**\n"
    f"- Create a full detailed day-by-day itinerary based on the trip duration. Include suggested times for activities listed above, when yuou recommend restaurants, pick from the given ones. "
    f"transportation tips, and meal recommendations. When you recommend a actvitity make sure the restaurant for lunch on that day location is close, rememeber, you are given the gps co-ordinates.\n"
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
        max_tokens=2000,
        temperature=0.7,
        )
        travel_plan = response.choices[0].message.content
        return travel_plan
    
    except Exception as e:
        print("Api error with openai : ", e)
        return "Error with Openai Gpt-3"

@app.route('/api/flights', methods=['POST'])
def flights():
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

    response = {
        "status": "success",
        "message": "Travel details received",
        "details": {
            "flights": flights,
        }
    }
    return jsonify(response)


@app.route('/api/hotels', methods=['POST'])
def hotels():
    data = request.get_json()
    destination = data.get('destination_city')
    number_of_people = data.get('number_of_people')
    budget = data.get('budget_range')
    depart_date = data.get('departure_date')
    return_date = data.get('return_date')
    flight_price = data.get('flight_price')
    price_per_person_per_day = int(data.get('price_per_person_per_day'))

    d1 = datetime.strptime(str(depart_date), "%Y-%m-%d")
    d2 = datetime.strptime(str(return_date), "%Y-%m-%d")
    duration = (d2 - d1).days

    print("getting coords for: ", destination)
    
    total_extra_cost = int(price_per_person_per_day)*int(duration)*int(number_of_people)
    print("total extra: ", total_extra_cost, "flight: ", flight_price)
    per_night_budget = ((int(budget - int(flight_price))) - (total_extra_cost))/int(duration)
    hotels = get_hotel_data(destination,str(depart_date), str(return_date), number_people=number_of_people)
    print("hotels: ", hotels)

    best_hotels = []
    min_price_diffs = []
    hotel_info = ""  # Initialize the variable before appending to it
    print("total extra: ", total_extra_cost, "flight: ", flight_price)
    print("per night budget: ", per_night_budget)
    # Find the four hotels with prices closest to the budget
    for hotel in hotels:
        if hotel['price'] == 0:
            continue
        hotel_info += f"- **{hotel['name']}**\n"
        hotel_info += f"  - Price: {hotel['price'] * (duration - 1)}\n"
        hotel_info += f"  - [Click here to book]({hotel['url']})\n"

        price = int(float(hotel['price']))
        price_diff = abs(per_night_budget - price)

        # Add each hotel to the list with its price difference
        min_price_diffs.append((hotel, price_diff))

    # Sort by price difference and select the top 4
    min_price_diffs = sorted(min_price_diffs, key=lambda x: x[1])[:4]

    best_hotels = [
    [hotel['name'], hotel['price'], hotel['url'], hotel['coords'], hotel['picture'], hotel['rating'], hotel['description'], hotel['amenities'], hotel['location_rating']] 
    for hotel, diff in min_price_diffs
]
    
    print(best_hotels)
    response = {
        "status": "success",
        "message": "Travel details received",
        "details": {
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
    price_per_person_per_day = int(data.get('price_per_person_per_day'))




    weather = get_average_temp(destination, depart_date)
    lat= hotels[3]['latitude']
    lng = hotels[3] ['longitude']


    res = get_restaurants(destination, lat, lng)


    activities = get_activities(destination, lat, lng)
    activities_array  = []
    for activity in activities:
        url = get_website((str(activity)+" tickets"))
        activities_array.append([activity, url])



    d1 = datetime.strptime(str(depart_date), "%Y-%m-%d")
    d2 = datetime.strptime(str(return_date), "%Y-%m-%d")
    duration = (d2 - d1).days

    cost = 0  
    per_person_cost = int(number_of_people)*price_per_person_per_day*int(duration)
    cost = cost + int(hotels[1]*int(duration)) + int(flights['price']) + int(per_person_cost)

    ai_response = get_openai_response(number_of_people=number_of_people, departure=departure, destination=destination, duration=duration, flights=flights, weather_info=weather, best_hotels=hotels, activities=activities_array, restaurants=res, cost=cost, budget=budget, per_person_cost=per_person_cost)


    response = {
        "status": "success",
        "message": "response",
        "details": {
            "response": ai_response,
            "activities": activities_array,
            "restaurants": res,
        }
    }
    return jsonify(response)





@app.route('/api/send_email', methods=['POST'])
def send_email():
    data = request.get_json()
    user_email = data.get('user_email')
    message = data.get('message').get('response')


    sender_email = "rafayellatif19@gmail.com"
    receiver_email = user_email
    password = "ulfl vgfa vjvx znsp"

    print(message)
    processed_ai_response = preprocess_markdown(message)

    # Convert Markdown to HTML
    html_content = markdown2.markdown(processed_ai_response)

    # Email setup
    msg = MIMEMultipart("alternative")
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "AI Travel Plan!"

    # Attach both plain text and HTML versions
    msg.attach(MIMEText(processed_ai_response, "plain"))  # Plain text version
    msg.attach(MIMEText(html_content, "html"))  # HTML version

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Markdown email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()


    response = {
        "status": "success",
        "message": "response",
        "details": {
            "response": "Email sent",
        }
    }
    return jsonify(response)


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        # Check if the user already exists
        user = auth.get_user_by_email(email)
        return jsonify({"message": "User already exists", "uid": user.uid}), 400
    except auth.UserNotFoundError:
        # Create new user
        user = auth.create_user(email=email, password=password)
        return jsonify({"message": "User created", "uid": user.uid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        # Since password validation is done client-side, we just fetch user info here
        user = auth.get_user_by_email(email)
        return jsonify({"message": f"Hello {user.email}", "uid": user.uid}), 200
    except auth.UserNotFoundError:
        return jsonify({"error": "User not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    


    
@app.route('/api/save_trip', methods=['POST'])
def save_trip():
    print("hello")
    try:
        # Parse the request JSON
        data = request.json
        required_fields = ["user_email", "destination_city", "departure_city", "selected_flights", 
                           "selected_hotel", "restaurants", "activities"]
        
        # Validate required fields
        for field in required_fields:
            if field not in data:
                print(f"Missing field: {field}")
                return jsonify({"error": f"Missing required field: {field}"}), 400
                
                # Prepare trip data for Firestore
        h = data["selected_hotel"]
        print(h)
        hotel  = [
            {
                "name": h[0],
                "price": h[1],
                "website": h[2],


            }
        ]

        print(hotel)
        restaurants = [
            {
                "name": r[0],
                "website": r[1],
                "location": r[2]
            }
            for r in data["restaurants"]
        ]

        activities = [
            {
                "name": a[0][0],
                "website": a[0][1],
                "location": a[0][2],
                "additional_info": a[1] if len(a) > 1 else None
            }
            for a in data["activities"]
        ]
        print("hotel", hotel)
        # Save the transformed data
        trip_data = {
            "user_email": data["user_email"],
            "destination_city": data["destination_city"],
            "departure_city": data["departure_city"],
            "selected_flights": data["selected_flights"],
            "selected_hotel": hotel,
            "restaurants": restaurants,
            "activities": activities,
            "timestamp": firestore.SERVER_TIMESTAMP
        }

        print("saving trip data: ", trip_data)
        # Create a new document in the 'trips' collection
        doc_ref = db.collection('trips').add(trip_data)
        return jsonify({"message": "Trip saved successfully"}), 200
            
    except Exception as e:
        # Handle errors
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_trips', methods=['POST'])
def get_trips():

    # Get the user email from query parameters
    user_email = request.json["user_email"]
    print(user_email)
    if not user_email:
        return jsonify({"error": "Missing user_email parameter"}), 400
    
    # Query the Firestore collection for trips of the user
    trips_ref = db.collection('trips')
    user_trips_query = trips_ref.where('user_email', '==', user_email).stream()

    trips = []
    for trip in user_trips_query:
        trip_data = trip.to_dict()
        trip_data["id"] = trip.id  # Include the document ID for reference
        trips.append(trip_data)

    if not trips:
        return jsonify({"message": "No trips found for this user"}), 404

    print("trips", trips)
    return jsonify({"trips": trips}), 200




if __name__ == '__main__':
    app.run(debug=True)