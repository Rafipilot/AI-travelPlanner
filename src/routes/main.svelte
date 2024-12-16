<script>
  import { user } from './store';
  import axios from 'axios';
  import { onMount } from 'svelte';
  import { tick } from 'svelte';
  import flatpickr from 'flatpickr';
  import 'flatpickr/dist/flatpickr.css';
  
  let email = '';
  let password = '';
  let message = '';
  let isLoggedIn = false;
  let show_input_page = false;


  let destination_city = "";
  let departure_city = "";
  let number_of_people = 0;
  let budget = 10000;

  let departureDate = "";
  let returnDate = "";

  let show_itenerary = false
  let show_trip = false

  let isLoading = false;
  let apiResponse = null;
  let selectedFlight = null;
  let selectedHotel = null;
  let availableFlights = [];
  let availableHotels = [];
  let showGenerateButton = false;
  let aiResponsePage = false;
  let flightPage = false;
  let input_page = true; 
  let hotelPage = false;
  let cities = [];
  let Departure_searchQuery = "";
  let Destination_searchQuery = "";
  let showDepartureDropdown = false;
  let showDestinationDropdown = false;
  let show_dashboard = false;

  let price_per_person_per_day = 50;

  let confirmHotelButton;

  let activities = null;
  let restaurants = null;
  let docID = null;

  let cloud_trips = []

  let datePicker_min = new Date().toISOString().split("T")[0];

    onMount(async () => {
    
    const script = document.createElement('script');
    script.src = 'https://md-block.verou.me/md-block.js';
    script.type = 'module';
    script.onload = () => {
      console.log('md-block script loaded');
    };
    document.head.appendChild(script);
  });



  fetch('/cities.json')
    .then(response => {
      console.log(response); 
      return response.json();
    })
    .then(data => {
      console.log(data); 
      cities = data;
    })
    .catch(error => {
      console.error('Error loading cities:', error);
    });



  function toggle_input_page()  {
    show_input_page = true
    show_dashboard = false
  }
  function unflattenHotels(hotels) {
    if (!hotels || !Array.isArray(hotels)) {
        console.error("Invalid input for unflattening hotels");
        return [];
    }
    return hotels.map(hotel => [hotel.name, hotel.price, hotel.website]);
}
function unflattenActivities(activities) {
    // Validate input
    if (!activities || !Array.isArray(activities)) {
        console.error("Invalid input for unflattening activities");
        return [];
    }
    const activitiesArray = [];
    // Iterate through the activities array
    for (const activity of activities) {
        if (activity && typeof activity === 'object' && activity.name && activity.website) {
            const activityList = [activity.name, activity.website];
            
            activitiesArray.push(activityList);
        } else {
            console.warn("Invalid activity encountered", activity);
        }
    }
    return activitiesArray;
}

function unflattenRestaurants(res) {
    // Validate input
    if (!res || !Array.isArray(res)) {
        console.error("Invalid input for unflattening activities");
        return [];
    }

    // Create an array to store processed activities
    const r_array = [];

    // Iterate through the activities array
    for (const r of res) {
        if (r && typeof r === 'object' && r.name && r.website) {

            const r_list = [r.name, r.website];
            
            // Append to the result array
            r_array.push(r_list);
        } else {
            console.warn("Invalid activity encountered", r);
        }
    }

    return r_array;
}
  function get_cloud_trip(trip)  {
    selectedFlight = trip["selected_flights"]
    selectedHotel = trip["selected_hotel"]
    selectedHotel = unflattenHotels(selectedHotel)[0]
    console.log(selectedHotel)
    activities = unflattenActivities(trip["activities"])
    restaurants = unflattenRestaurants(trip["restaurants"])
    departure_city = trip["departure_city"]
    destination_city = trip["destination_city"]
    apiResponse = {"response": trip["ai_response"]}
    docID = trip["id"]
    departureDate = trip["departure_date"]
    returnDate = trip["return_date"]
    aiResponsePage = true
    show_dashboard = false
  }

  

  const selectDestinationCity = async (city) => {
    console.log("dest: ", city);
    destination_city = `${city.city}`;
    await tick(); 
    Destination_searchQuery = destination_city; 
  };

  const selectDepartureCity = async (city) => {
    departure_city = `${city.city}`;
    await tick();
    Departure_searchQuery = departure_city; 
  };

  

  async function generate() {
  console.log("Departure City: ", departure_city, "Destination City: ", destination_city);
  const travelData = {
    departure_city,
    destination_city,
    number_of_people,
    budget_range: Number(budget),
    departure_date: departureDate,
    return_date: returnDate,
    
  };
  if (!departure_city || !destination_city || !number_of_people) {
    alert("Please fill in all the required fields.");
    return; 
  }

  isLoading = true;
  try {
    const response = await fetch("https://my-svelte-project.onrender.com/api/flights", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(travelData)
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const result = await response.json();
    isLoading = false;
    availableFlights = result.details.flights || [];
    show_input_page = false // Hide input page
    flightPage = true; // show flight page
    hotelPage = false;  // hide hotel page
  } catch (error) {
    console.error("API request error:", error);
  } finally {
    isLoading = false;
  }
}

async function generateHotel() {
  console.log("Selected flight: ", selectedFlight);
  const hotelData = {
    departure_city,
    destination_city,
    number_of_people,
    budget_range: Number(budget),
    departure_date: departureDate,
    return_date: returnDate,
    flight_price: selectedFlight['price'],
    price_per_person_per_day: price_per_person_per_day,
  };

  if (!selectedFlight) {
    alert("Please select a flight first.");
    return; // Stop execution if no flight is selected
  }

  isLoading = true;
  try {
    const response = await fetch("https://my-svelte-project.onrender.com/api/hotels", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(hotelData)
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const result = await response.json();
    console.log(result)
    isLoading = false;
    availableHotels = result.details.best_hotels || [];
    hotelPage = true;  // Stay on hotel page
    flightPage = false; // Ensure flight page is hidden
  } catch (error) {
    console.error("API request error:", error);
  } finally {
    isLoading = false;
  }
}
async function GPT_response() {
  console.log("2ND CALL");

  const data = {
    selectedFlight,
    selectedHotel,
    departure_city,
    destination_city,
    number_of_people,
    departure_date: departureDate,
    return_date: returnDate,
    budget: budget,

    price_per_person_per_day: price_per_person_per_day,
  };

  isLoading = true;
  try {
    const response = await fetch("https://my-svelte-project.onrender.com/api/second_step", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const result = await response.json();
    apiResponse = result.details; 
    console.log(result)
    hotelPage = false; // Hide hotel page
    activities = apiResponse.activities
    restaurants = apiResponse.restaurants
    aiResponsePage = true; // Show AI response page

  } catch (error) {
    console.error("API request error:", error);
  } finally {
    isLoading = false;
  }
}

async function saveTrip() {
  const tripData = {
    user_email: email,
    destination_city,
    departure_city,
    selected_flights: selectedFlight,
    selected_hotel: selectedHotel,
    restaurants,
    activities,
    ai_response: apiResponse.response, 
    departure_date: departureDate,
    return_date: returnDate,
  };

  try {
    const response = await fetch("https://my-svelte-project.onrender.com/api/save_trip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tripData)
    });

    if (!response.ok) {
      throw new Error("Failed to save trip. Please try again.");
    }

    alert("Trip saved successfully!");
  } catch (error) {
    console.error("Error saving trip:", error);
    alert("An error occurred while saving the trip.");
  }
}

async function get_trips_and_return_to_dashboard() {
  const user_data = {
    user_email: email,
  }

  try {
    const response = await fetch("https://my-svelte-project.onrender.com/api/get_trips", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(user_data)
    });


  if (!response.ok) {
      throw new Error("Failed to save trip. Please try again.");
    }
    const result = await response.json();
    cloud_trips = result.trips
    console.log("wait")
    setTimeout(function(){
        console.log("THIS IS");
    }, 2000);
    console.log("show")
    show_dashboard = true
    aiResponsePage = false
    show_input_page = false

  } catch (error) {
    console.error("Error getting trip:", error);
    alert("An error occurred while getting trips.");
  }
}


async function get_trips()  {
  const user_data = {
    user_email: email,
  }

  try {
    const response = await fetch("https://my-svelte-project.onrender.com/api/get_trips", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(user_data)
    });


  if (!response.ok) {
      throw new Error("Failed to save trip. Please try again.");
    }
    const result = await response.json();
    console.log(result)
    cloud_trips = result.trips


  } catch (error) {
    console.error("Error getting trip:", error);
    alert("An error occurred while getting trips.");
  }
}
async function delete_trip()  {
  const user_data = {
    ID: docID,
  }

  try {
    const response = await fetch("https://my-svelte-project.onrender.com/api/delete_trip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(user_data)
    });


  if (!response.ok) {
      throw new Error("Failed to delete trip. Please try again.");
    }
    const result = await response.json();
    console.log(result)

    alert("Trip deleted successfully!");
  } catch (error) {
    console.error("Error deleting trip:", error);
    alert("An error occurred while deleting trips.");
  }
}


  $: filteredDepartureCities = cities
    .filter(city => 
      city.city.toLowerCase().includes(Departure_searchQuery.toLowerCase()) ||
      city.country.toLowerCase().includes(Departure_searchQuery.toLowerCase())
    )
    .slice(0, 50); // Show only the top 50 results

  $: filteredDestinationCities = cities
    .filter(city => 
      city.city.toLowerCase().includes(Destination_searchQuery.toLowerCase()) ||
      city.country.toLowerCase().includes(Destination_searchQuery.toLowerCase())
    )
    .slice(0, 50);

    function handleNumberPeopleChange(event) {
    number_of_people = event.target.value;
  }

  function handleBudgetChange(event) {
    budget = event.target.value;
  }
  function handlePricePerPerson(event)  {
    price_per_person_per_day = event.target.value;
  }

  function handleFlightSelection(event) {
    const selectedFlightIndex = event.target.value;
    selectedFlight = availableFlights[selectedFlightIndex];
    console.log("Selected flight:", selectedFlight);
  }

  function handleHotelSelection(event) {
    const selectedHotelIndex = event;
    selectedHotel = availableHotels[selectedHotelIndex];
    console.log("Selected hotel:", selectedHotel);
    showGenerateButton = selectedFlight && selectedHotel;

    // Scroll to the confirm button
    tick().then(() => {
      if (confirmHotelButton) {
        confirmHotelButton.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
  }

  const registerUser = async () => {
    isLoading = true
    try {
      const response = await axios.post('https://my-svelte-project.onrender.com/register', {
        email,
        password
      });
      isLoading = false
      message = response.data.message;
    } catch (error) {
      isLoading = false;
      message = error.response.data.error;
    }
  };

  const loginUser = async () => {
    isLoading = true
    try {
      const response = await axios.post('https://my-svelte-project.onrender.com/login', {
        email,
        password
      });
      message = response.data.message;
      user.set(response.data);  // Set the user data in the store
      get_trips()
      isLoggedIn = true;
      isLoading = false;
      show_dashboard = true;
      
    } catch (error) {
      isLoading = false;
      message = error.response.data.error;
    }
  };

 
</script>

<main>
  {#if !isLoggedIn}
    
    <h1>Login / Register</h1>
    <input bind:value={email} placeholder="Email" type="email" />
    <input bind:value={password} placeholder="Password" type="password" />
    <button on:click={loginUser} id="general_button">Login</button>
    <button on:click={registerUser} id="general_button">Register</button>
    <p>{message}</p>
  {:else}
  {#if show_dashboard}
  <h1>Hi {email}</h1>
  <h2 id = "central_subheader">Your trips</h2>
  <button on:click={toggle_input_page} id="general_button">Plan a new trip</button>
  <div id="dashboard-container">
    {#if cloud_trips && cloud_trips.length > 0}
    <div id="trips-container">
      {#each cloud_trips as trip, index}
        <div class="trip-box" on:click={() => get_cloud_trip(trip)}>
          <h3>{trip.destination_city}</h3>
          <p>Click to view trip details</p>
        </div>
      {/each}
    </div>
  {:else}
    <div class="trip-box no-trip">
      <p>No trips planned yet.</p>
      <button on:click={toggle_input_page} id="general_button">Plan a new trip</button>
    </div>
  {/if}
  </div>
{/if}
    {#if show_input_page}

    <div id="mainPage">
      <h1>Travel Details</h1>
      <button on:click={get_trips_and_return_to_dashboard} id="general_button">Back to dashboard</button>

      <div class="search-container">
        <h4>Step 1: Enter your departure city</h4>
        <input
          type="text"
          bind:value="{Departure_searchQuery}"
          placeholder="{departure_city === '' ? 'Search departure cities...' : departure_city}"
          on:focus="{() => showDepartureDropdown = true}"
          on:blur="{() => setTimeout(() => showDepartureDropdown = false, 200)}"
        />
        
        {#if showDepartureDropdown && filteredDepartureCities.length > 0}
          <ul class="dropdown">
            {#each filteredDepartureCities as city}
              <li
                on:mousedown="{() => selectDepartureCity(city)}"
              >
                {city.city}, {city.country}
              </li>
            {/each}
          </ul>
        {/if}
        <!-- Destination Search -->
        <h4>Step 2: Enter your destination city</h4>
        <input
          type="text"
          bind:value="{Destination_searchQuery}"
          placeholder="{destination_city === '' ? 'Search destination cities...' : destination_city}"
          on:focus="{() => showDestinationDropdown = true}"
          on:blur="{() => setTimeout(() => showDestinationDropdown = false, 200)}"
        />
        
        {#if showDestinationDropdown && filteredDestinationCities.length > 0}
          <ul class="dropdown">
            {#each filteredDestinationCities as city}
              <li
                on:mousedown="{() => selectDestinationCity(city)}"
              >
                {city.city}, {city.country}
              </li>
            {/each}
          </ul>
        {/if}
        
              </div>  
              </div>
              
        
          <h4>Step 3: Number of People</h4>
          <input type="number" placeholder="Number of People" bind:value="{number_of_people}" on:input="{handleNumberPeopleChange}" />
        
          <h4>Step 4: Budget (Flights, Hotels, Per Person Daily Extras)</h4>
          <input type="range" min="100" max="20000" step="100" bind:value="{budget}" on:input="{handleBudgetChange}" />
          <span>{budget}$</span>

          <h4>Step 5: Per Person Daily Extras (Meals, Taxis, Activities, etc)</h4>
          <input type="range" min="20" max="200" step="10" bind:value="{price_per_person_per_day}" on:input="{handlePricePerPerson}" />
          <span>{price_per_person_per_day}$</span>
        
          <h4>Step 6: Travel Dates</h4>
          <label for="departure-date">Departure Date:</label>
          <input id="departure-date" type="date" bind:value="{departureDate}" min={datePicker_min}/>
        
          <label for="return-date">Return Date:</label>
          <input id="return-date" type="date" bind:value="{returnDate}" min={departureDate} />
          
        
          <button on:click="{generate}" id="start_button">Ask your personalized travel agent</button>
        
          {/if}

          {#if flightPage && !isLoading}
          <div id="mainPage">
            <h1>Choose Your Flight</h1>
    
            <h4>Select a Flight</h4>
            <select on:change="{handleFlightSelection}">
              <option value="">-- Select a Flight --</option>
              {#each availableFlights as flight, index}
              <option value="{index}">
                {#if flight.airlines && Array.isArray(flight.airlines)}
                  {flight.airlines.join(", ")} - {flight.price}$
                {:else}
                  No airlines available - {flight.price}$
                {/if}
              </option>
              {/each}
            </select>
    
            <button on:click="{generateHotel}" disabled="{isLoading}" id = "start_button">Generate Hotels</button>
          </div>
        {/if}
    
      {#if hotelPage && !isLoading}
      <div id="hotelPage">
        <h1>Select a Hotel</h1>
        {#if availableHotels && availableHotels.length > 0}
          <ul id="hotelList">
            {#each availableHotels as hotel, index}
              <li class="hotel-item">
                <div class="hotel-info">
                  <span class="hotel-name">{hotel[0]} - {hotel[1]}$ per night</span>
                  <div class="hotel-image-container">
                    <img class="hotel-image" src="{hotel[4]}" alt="Hotel Image" />
                  </div>
                  <span>Rating: {hotel[5]}</span>
                  <span>Description: {hotel[6]}</span>
                  <ul id="a_list">
                    {#each hotel[7] as amenity, index}
                      <span>{amenity}</span>
                    {/each}
                  </ul>
                </div>
                <button class="select-button"
                  on:click={() => handleHotelSelection(index)} 
                  aria-label="Select {hotel[0]}"
                >
                  Select
                </button>
              </li>
            {/each}
          </ul>
          <button id="start_button" bind:this={confirmHotelButton} on:click={GPT_response}>
            {selectedHotel ? `Confirm ${selectedHotel[0]}` : 'Confirm Selection'}
          </button>
        {:else}
          <p>No hotels available. Please try again later.</p>
        {/if}
      </div>
    {/if}
    
    {#if aiResponsePage && !isLoading}
    <div id="responsePage">
      <h1 id="">Your Trip</h1>
      
      <button on:click={saveTrip} id="general_button">Save Trip</button>
      <button on:click={delete_trip} id="general_button">Delete Trip</button>
      <button on:click={get_trips_and_return_to_dashboard} id="general_button">Back to dashboard</button>
      <h2>{departure_city} to {destination_city}</h2>
      <h4>{departureDate} to  {returnDate}</h4>
      <div class="flex-container">
        
        <!-- Flights Section -->
        <div id="flights" class="infoBox">
          <h3 class="sectionHeader">Flights</h3>
          <div class="infoContent">
            <h4>Airlines:</h4>
            <ul>
              {#each selectedFlight.airlines as airline}
                <li>{airline}</li>
              {/each}
            </ul>
            <p><strong>Price:</strong> ${selectedFlight.price}</p>
            <p><strong>URL:</strong> <a href="{selectedFlight.url}" target="_blank">View Flight</a></p>
          </div>
        </div>
        
        <!-- Hotels Section -->
        <div id="hotels" class="infoBox">
          <h3 class="sectionHeader">Hotels</h3>
          <div class="infoContent">
            <h4>{selectedHotel[0]}</h4>
            <p><strong>Price(Per Night):</strong> ${selectedHotel[1]}</p>
            <p><strong>Website:</strong> <a href="{selectedHotel[2]}" target="_blank">View Hotel</a></p>
          </div>
        </div>
        
        <!-- Activities Section -->
        <div id="activities" class="infoBox">
          <h3 class="sectionHeader">Activities</h3>
          <div class="infoContent">
            <ul class="scrollable-list">
              {#each activities as activity}
                <li>{activity[0]}</li>
                <li><a href={activity[1]}>Website</a></li>
              {/each}
            </ul>
          </div>
        </div>
  
        <!-- Restaurants Section -->
        <div id="restaurants" class="infoBox">
          <h3 class="sectionHeader">Recommended Restaurants</h3>
          <div class="infoContent">
            <ul class="scrollable-list">
              {#each restaurants as res}
                <li>{res[0]}</li>
                <li><a href={res[1]}>Website</a></li>
              {/each}
            </ul>
          </div>
        </div>
      </div>
  
      <!-- Itinerary Section -->
      <div id="itinerary_container">
        <h2>Travel Itinerary</h2>
        <div class="itinerary-details">
          <strong>AI Response:</strong>
          <md-block>
            <strong>AI Response:</strong>
            ${apiResponse.response}
          </md-block>
        </div>
      </div>
    </div>

    {/if}
  {/if}
  {#if isLoading}
  <div class="spinner"></div>
  <p id="loading_text">Loading, this could take 1-2 minutes</p>
{/if}
</main>

