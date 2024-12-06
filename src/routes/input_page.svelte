<script>
  import { onMount } from 'svelte';
  import { tick } from 'svelte';

  let destination_city = "";
  let departure_city = "";
  let number_of_people = 0;
  let budget = 10000;
  let departureDate = "";
  let returnDate = "";
  let isLoading = false;
  let apiResponse = null;
  let selectedFlight = null;
  let selectedHotel = null;
  let availableFlights = [];
  let availableHotels = [];
  let showGenerateButton = false;
  let showAIResponse = false;
  let aiResponsePage = false;
  let flightPage = false;
  let input_page = true; 
  let hotelPage = false;
  let cities = [];
  let Departure_searchQuery = "";
  let Destination_searchQuery = "";
  let filteredCities = [];
  let showDepartureDropdown = false;
  let showDestinationDropdown = false;
  let user_email = "";
  let flight_price = 0

  fetch('/cities.json')
    .then(response => {
      console.log(response); // Log the response to inspect it
      return response.json();
    })
    .then(data => {
      console.log(data); // Log the parsed data to check the structure
      cities = data;
    })
    .catch(error => {
      console.error('Error loading cities:', error);
    });

    onMount(async () => {
    const script = document.createElement('script');
    script.src = 'https://md-block.verou.me/md-block.js';
    script.type = 'module';
    script.onload = () => {
      console.log('md-block script loaded');
    };
    document.head.appendChild(script);
  });

  const selectDestinationCity = async (city) => {
    console.log("dest: ", city);
    destination_city = `${city.city}`;
    await tick(); // Ensure DOM is updated before changing the searchQuery
    Destination_searchQuery = destination_city; // Update the input value
  };

  const selectDepartureCity = async (city) => {
    departure_city = `${city.city}`;
    await tick(); // Ensure DOM is updated before changing the searchQuery
    Departure_searchQuery = departure_city; // Update the input value
  };

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

  function handleEmailChange(event) {
    user_email = event.target.value;
    console.log(user_email);
  }

  function handleBudgetChange(event) {
    budget = event.target.value;
  }

  function handleDepartureDateChange(event) {
    departureDate = event.target.value;
  }

  function handleReturnDateChange(event) {
    returnDate = event.target.value;
  }



  function handleFlightSelection(event) {
    const selectedFlightIndex = event.target.value;
    selectedFlight = availableFlights[selectedFlightIndex];
    console.log("Selected flight:", selectedFlight);
  }

  function handleHotelSelection(event) {
    const selectedHotelIndex = event.target.value;
    selectedHotel = availableHotels[selectedHotelIndex];
    console.log("Selected hotel:", selectedHotel);
    showGenerateButton = selectedFlight && selectedHotel;
  }


  async function generate() {
  console.log("Departure City: ", departure_city, "Destination City: ", destination_city);
  const travelData = {
    departure_city,
    destination_city,
    number_of_people,
    budget_range: Number(budget),
    departure_date: departureDate,
    return_date: returnDate
  };
  if (!departure_city || !destination_city) {
    alert("Please fill in both the departure city and the destination city.");
    return; // Stop execution if inputs are invalid
  }

  isLoading = true;
  try {
    const response = await fetch("http://127.0.0.1:5000/api/flights", {
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
    input_page = false // Hide input page
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
  };

  if (!selectedFlight) {
    alert("Please select a flight first.");
    return; // Stop execution if no flight is selected
  }

  isLoading = true;
  try {
    const response = await fetch("http://127.0.0.1:5000/api/hotels", {
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
    user_email: user_email,
  };

  isLoading = true;
  try {
    const response = await fetch("http://127.0.0.1:5000/api/second_step", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const result = await response.json();
    apiResponse = result.details; // Assign the details to the apiResponse
    hotelPage = false; // Hide hotel page
    aiResponsePage = true; // Show AI response page
    console.log(apiResponse);
  } catch (error) {
    console.error("API request error:", error);
  } finally {
    isLoading = false;
  }
}

</script>

<main>
  {#if input_page && !isLoading}
    <div id="mainPage">
      <h1>Travel Details</h1>

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
        <h4>Step 2: Enter your detination city</h4>
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
        
          <h4>Step 4: Budget</h4>
          <input type="range" min="100" max="20000" bind:value="{budget}" on:input="{handleBudgetChange}" />
          <span>{budget}$</span>
        
          <h4>Step 5: Travel Dates</h4>
          <input type="date" bind:value="{departureDate}" on:input="{handleDepartureDateChange}" />
          <input type="date" min="{departureDate}" bind:value="{returnDate}" on:input="{handleReturnDateChange}" />
        
          <h4>Step 6: Optionally enter your email address so we can send a copy of your personalized travel plan straight to your inbox</h4>
          <input type="email" placeholder="youremail@example.com" bind:value="{user_email}" on:input="{handleEmailChange}"/>
        
          <button on:click="{generate}" id="start_button">Ask your personalized travel agent</button>
        
          {/if}


    {#if flightPage && !isLoading}
      <div id="mainPage">
        <h1>Choose Your Flight</h1>

        <h4>Step 6: Select a Flight</h4>
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

        <button on:click="{generateHotel}" disabled="{isLoading}">Generate Hotels</button>
      </div>
    {/if}

    {#if hotelPage && !isLoading}
    <div id="hotelPage">
      <h1>Select a Hotel</h1>
      <select id="hotelSelect" on:change="{handleHotelSelection}">
        <option value="">-- Select a Hotel --</option>
        {#each availableHotels as hotel, index}
          <option value="{index}">{hotel[0]} - {hotel[1]}$ per night</option>
        {/each}
      </select>
      <button on:click="{GPT_response}" disabled="{!showGenerateButton}">Generate Itinerary</button>
    </div>
  {/if}

  {#if aiResponsePage && !isLoading}
    <div id="responsePage">
      <h1>Personalized Travel Itinerary</h1>
        <md-block>
          <strong>AI Response:</strong>
          ${apiResponse.response}
        </md-block>
    </div>
  {/if}

  {#if isLoading}
    <div class="spinner"></div>
    <p id="loading_text">Loading, this could take up to 3 minutes</p>
  {/if}
</main>
