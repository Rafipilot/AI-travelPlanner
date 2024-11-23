import urllib.parse

def generate_hotel_affiliate_link(hotel_name, start_date, end_date, affiliate_id):
    base_url = "https://www.expedia.com/Hotel-Search"
    # This should be the unique identifier for the hotel (usually the hotel's ID or URL-friendly name).
    # For simplicity, we will assume the hotel_name is a URL-friendly version of the name.
    hotel_identifier = hotel_name.lower().replace(" ", "-")  # Simple transformation for the hotel name
    
    params = {
        "hotel": hotel_identifier,  # Hotel name or ID
        "startDate": start_date,
        "endDate": end_date,
        "affiliate_id": affiliate_id,
    }
    
    # Build the full URL with parameters
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return url

# Example usage
hotel_name = "Hotel Rafayel"
start_date = "2024-12-01"  # YYYY-MM-DD format
end_date = "2024-12-10"
affiliate_id = "10111378633"

affiliate_link = generate_hotel_affiliate_link(hotel_name, start_date, end_date, affiliate_id)
print(f"Generated Expedia Affiliate Link: {affiliate_link}")


