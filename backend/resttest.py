from serpapi import GoogleSearch
import re
import os
from dotenv import load_dotenv

load_dotenv()

ser_api_key = os.getenv("SER_API_KEY")

def get_hotel_data(city_name, checkin="2024-12-15", checkout="2024-12-20", number_people="2"):
    try:
        # Define parameters for the request
        params = {
            'engine': 'google_hotels',
            'q': f"Hotels in {city_name}",
            'check_in_date': checkin,
            'check_out_date': checkout,
            'adults': number_people,
            'api_key': ser_api_key,
        }

        search = GoogleSearch(params)
        results = search.get_dict()  # Get the JSON response as a dictionary
        
        # Print the entire response for debugging
        print("API Response:", results)

        # Check if 'properties' exists in the response
        if 'properties' not in results or not results['properties']:
            print("No properties found in response.")
            return []

        # Extract hotel data from the response
        hotels = []
        for property in results['properties']:
            # Extract and clean price information
            price_string = property.get('rate_per_night', {}).get('lowest', 'Price not available')
            price_clean = re.sub(r'[^\d.]', '', price_string)  # Remove non-numeric characters

            try:
                price = float(price_clean)
            except ValueError:
                price = None  # Handle cases where price conversion fails

            # Build the hotel data dictionary
            hotel_data = {
                'name': property.get('name', 'No name available'),
                'price': price if price is not None else 0,
                'url': property.get('link', 'No URL available'),
                'coords': property.get('gps_coordinates', {}),
                'picture': property.get('images', [{}])[0].get('thumbnail', 'No picture available'),
            }
            hotels.append(hotel_data)

        # Check if hotels were found
        if hotels:
            print("Hotels found:", hotels)
            return hotels
        else:
            print("No hotels found with the provided query.")
            return []
    except Exception as e:
        print("Error with SerpAPI:", e)
        return []

# Test the function
hotels = get_hotel_data("Malé")
print("Final Hotel Data:", hotels)
