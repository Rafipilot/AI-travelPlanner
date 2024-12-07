from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_hotel_data(city, checkin, checkout):
    url = f"https://www.booking.com/searchresults.html?ss={city}&ssne={city}&ssne_untouched={city}&checkin={checkin}&checkout={checkout}&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure&selected_currency=USD"
    
    # Set up Selenium options
    options = Options()
    options.headless = True  # Run browser in headless mode (without GUI)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Load the page
    driver.get(url)
    
    # Wait for the page to load
    driver.implicitly_wait(10)  # Wait for up to 10 seconds for elements to load
    
    # Get the page source after it's fully rendered
    html = driver.page_source
    print(html)  # Output the page source for debugging

    driver.quit()  # Close the browser
    
    soup = BeautifulSoup(html, 'html.parser')
    hotels = soup.find_all('div', {'data-testid': 'property-card'})
    hotels_data = []
    
    for hotel in hotels:
        name = hotel.find('div', {'data-testid': 'title'}).text.strip() if hotel.find('div', {'data-testid': 'title'}) else "N/A"
        location = hotel.find('span', {'data-testid': 'address'}).text.strip() if hotel.find('span', {'data-testid': 'address'}) else "N/A"
        
        # Try to get the price
        price_tag = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
        if price_tag:
            price = price_tag.text.strip()
        else:
            price = "N/A"  # Default if no price is found

        hotels_data.append({'name': name, 'location': location, 'price': price})
    
    return hotels_data

print(get_hotel_data("London", "10/12/24", "15/12/24"))
