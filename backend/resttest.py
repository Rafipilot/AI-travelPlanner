import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown2

# Email details
sender_email = "rafayellatif19@gmail.com"
receiver_email = "rafayel.latif@gmail.com"
password = "ulfl vgfa vjvx znsp"  # Use an App Password if applicable

# Function to preprocess Markdown
def preprocess_markdown(content):
    # Add double spaces at the end of bullet points for proper line breaks
    lines = content.splitlines()
    processed_lines = []
    for line in lines:
        if line.strip().startswith(("-", "*")):  # Bullet points
            processed_lines.append(line + "  ")  # Add double space for line break
        else:
            processed_lines.append(line)
    return "\n".join(processed_lines)

# Markdown content generated dynamically (example placeholder)
markdown_content = """
**Travel Plan for Jakarta to London**

**Trip Overview:**
- Trip Duration: 6 days
- Number of Travelers: 4
- Departure Location: Jakarta
- Destination Location: London
- Budget: $7563

**Flight Information:**
- Airline: Qatar Airways
- Price: $4894 (Return tickets)
- Flight Details: Departure from Jakarta to London with Qatar Airways. The flight duration is approximately 15 hours with a layover in Doha.

- [Book your flight here](https://www.qatarairways.com/en-us/homepage.html)

**Weather Info:**
- The average temperature in London during December is 7°C. Pack warm clothing, including coats, scarves, and gloves to stay comfortable during your trip.

**Hotel Recommendation:**
- Stay at [Holiday Inn Express London - Croydon](https://www.ihg.com/holidayinnexpress/hotels/gb/en/london/loncr/hoteldetail?cm_mmc=GoogleMaps-_-EX-_-GB-_-LONCR)
- Price: $226 per night

**Restaurant Options near Hotel:**
- Nando's Croydon - High Street
- Fern
- Mithras Turkish Mediterranean Restaurant
- Saigon Bleu 西貢
- Wagamama Croydon
- Rio Lounge - South Indian and Sri Lankan Restaurant
- Aqua Bar & Grill - Croydon
- Pizza Express
- Nando's East Croydon
- Roosters Piri Piri Croydon
- Wei Dao Chinese Restaurant
- The Greek Corner
- Crown & Pepper Croydon
- Basil & Grape
- Atesh Turkish Restaurant (Croydon)

**Activities and Attractions:**
1. South Norwood Lake & Grounds - Enjoy a large park with various activities like sailing, fishing, and tennis. [More Info](https://www.croydon.gov.uk/libraries-leisure-and-culture/parks-and-open-spaces/parks-and-playgrounds/parks-and-playgrounds-directory/south-norwood-lake-and-grounds)
2. Croydon Airport Visitor Centre - Explore a small museum in a historic air traffic control tower. [More Info](https://www.historiccroydonairport.org.uk/opening-hours/)

**Day-by-Day Itinerary:**

**Day 1: Arrival in London**
- Check into Holiday Inn Express London - Croydon
- Dinner at Nando's Croydon - High Street

**Day 2: Explore Croydon**
- Breakfast at the hotel
- Visit South Norwood Lake & Grounds
- Lunch at Mithras Turkish Mediterranean Restaurant
- Explore Croydon Airport Visitor Centre
- Dinner at Atesh Turkish Restaurant (Croydon)

**Day 3: London Sightseeing**
- Travel to central London
- Visit popular attractions like Buckingham Palace, Big Ben, and the London Eye
- Lunch at a local restaurant
- Dinner at Aqua Bar & Grill - Croydon

**Day 4: Cultural Day**
- Breakfast at the hotel
- Explore Croydon's museums like Museum of Croydon
- Lunch at Fern
- Visit Croydon Minster
- Dinner at The Greek Corner

**Day 5: Nature Day**
- Breakfast at the hotel
- Spend the day at Lloyd Park
- Lunch at Wei Dao Chinese Restaurant
- Explore Wandle Park
- Dinner at Roosters Piri Piri Croydon

**Day 6: Departure**
- Check out of the hotel
- Travel to the airport for your return flight to Jakarta

**Budget Breakdown:**
- Flights: $4894
- Hotels: $1356
- Meals and activities: $1200
- Total: $7450

**Additional Tips:**
- Use public transportation like the Tube to get around London efficiently.
- Be prepared for rain in London, so pack an umbrella.
- Respect local customs and etiquette, such as forming orderly queues.
- Enjoy traditional British dishes like fish and chips or a Sunday roast during your stay.

"""

# Preprocess the Markdown content
processed_markdown = preprocess_markdown(markdown_content)

# Convert Markdown to HTML
html_content = markdown2.markdown(processed_markdown)

# Email setup
msg = MIMEMultipart("alternative")
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = "Markdown Email Test5"

# Attach both plain text and HTML versions
msg.attach(MIMEText(processed_markdown, "plain"))  # Plain text version
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
