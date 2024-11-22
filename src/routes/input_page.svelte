<script>
  import { onMount } from 'svelte';

  onMount(() => {
      const script = document.createElement('script');
      script.src = 'https://md-block.verou.me/md-block.js';
      script.type = 'module';
      script.onload = () => {
        console.log('md-block script loaded');
      };
      document.head.appendChild(script);
    });


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
  let aiResponsePage = false; // New flag for navigating to the AI response page

  function handleDepartureCityChange(event) {
    departure_city = event.target.value;
  }

  function handleDestinationCityChange(event) {
    destination_city = event.target.value;
  }

  function handleNumberPeopleChange(event) {
    number_of_people = event.target.value;
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
    };

    isLoading = true;
    try {
      const response = await fetch("https://tpfrontend-ozcx.onrender.com/api/second_step", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const result = await response.json();
      apiResponse = result.details; // Assign the details to the apiResponse
      aiResponsePage = true; // Switch to the AI response page
      console.log(apiResponse);
    } catch (error) {
      console.error("API request error:", error);
    } finally {
      isLoading = false;
    }
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
      const response = await fetch("https://tpfrontend-ozcx.onrender.com/api/first_step", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(travelData)
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const result = await response.json();
      isLoading = false;
      apiResponse = result.details;
      console.log(apiResponse); // Log for debugging
      availableFlights = apiResponse.flights || [];
      availableHotels = apiResponse.best_hotels || [];
    } catch (error) {
      console.error("API request error:", error);
    } finally {
      isLoading = false;
    }
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

    showGenerateButton = (selectedFlight && selectedHotel);
  }
</script>

<main>
  {#if !apiResponse && !aiResponsePage}
    <div id="mainPage">
      <h1>Travel Details</h1>
      <h4>Step 1: Select Departure City</h4>
      <input type="text" placeholder="Enter Departure City" bind:value="{departure_city}" on:input="{handleDepartureCityChange}" />

      <h4>Step 2: Select Destination City</h4>
      <input type="text" placeholder="Enter Destination City" bind:value="{destination_city}" on:input="{handleDestinationCityChange}" />

      <h4>Step 3: Number of People</h4>
      <input type="number" placeholder="Number of People" bind:value="{number_of_people}" on:input="{handleNumberPeopleChange}" />

      <h4>Step 4: Budget</h4>
      <input type="range" min="100" max="20000" bind:value="{budget}" on:input="{handleBudgetChange}" />
      <span>{budget}$</span>

      <h4>Step 5: Travel Dates</h4>
      <input type="date" bind:value="{departureDate}" on:input="{handleDepartureDateChange}" />
      <input type="date" min="{departureDate}" bind:value="{returnDate}" on:input="{handleReturnDateChange}" />

      <button on:click="{generate}">Ask your personalized travel agent</button>
    </div>
  {/if}

  {#if isLoading}
    <div class="spinner"></div>
  {/if}

  {#if apiResponse && !aiResponsePage}
    <div id="responsePage">
      <h2>Your Travel Details</h2>

      <!-- Flights Section -->
      <div id="flightSection">
        <h3>Select a Flight</h3>
        <select id="flightSelect" on:change="{handleFlightSelection}">
          <option value="">-- Select a Flight --</option>
          {#each availableFlights as flight, index}
            <option value="{index}">{flight.airlines.join(", ")} - {flight.price}$</option>
          {/each}
        </select>
      </div>

      <!-- Hotels Section -->
      <div id="hotelSection">
        <h3>Select a Hotel</h3>
        <select id="hotelSelect" on:change="{handleHotelSelection}">
          <option value="">-- Select a Hotel --</option>
          {#each availableHotels as hotel, index}
            <option value="{index}">{hotel[0]} - {hotel[1]}$ per night</option>
          {/each}
        </select>
      </div>

      {#if showGenerateButton}
        <button on:click="{GPT_response}">Generate</button>
      {/if}
    </div>
  {/if}

  {#if aiResponsePage}
    <div id="aiResponsePage">
      <h2>AI's Personalized Recommendation:</h2>
      <md-block>
        <strong>AI Response:</strong>
        ${apiResponse.response}
      </md-block>
    </div>
  {/if}
</main>
