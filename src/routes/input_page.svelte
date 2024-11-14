

<script>
    import { active } from 'd3';
  import { onMount } from 'svelte';

  onMount(() => {
    const script = document.createElement('script');
    script.src = 'https://md-block.verou.me/md-block.js';
    script.type = 'module';
    script.onload = () => {
      // You can now use <md-block> after the script is loaded
      console.log('md-block script loaded');
    };
    document.head.appendChild(script);
  });
  
  let destination_airport = "";
  let departure_airport = "";
  let number_of_people = 0;
  let budgetRange = [100, 20000];
  let departureDate = "";
  let returnDate = "";
  let airports = [];  // Array to store airport data
  let searchTermDeparture = "";  // Search term for departure airport
  let searchTermDestination = "";  // Search term for destination airport
  let destination_city = "";
  let apiResponse = null;  // Variable to store API response data

  // Fetch airport data from the provided URL
  async function fetchAirports() {
      const response = await fetch("https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat");
      const data = await response.text();
      const lines = data.split('\n');
      airports = lines.map(line => {
          const fields = line.split(',');
          
          // Check if the line has enough fields and ignore empty lines
          if (fields.length < 13) return null;  // Skip malformed lines
          
          return {
              name: fields[1]?.replace(/"/g, '') || '',  // Remove quotes
              city: fields[2]?.replace(/"/g, '') || '',
              country: fields[3]?.replace(/"/g, '') || '',
              code: fields[4]?.replace(/"/g, '') || ''
          };
      }).filter(Boolean);  // Remove any null entries (malformed lines)
  }

  // Filter airports based on search term
  function filteredAirports(searchTerm) {
      return airports.filter(airport => {
          const fullName = `${airport.name} (${airport.city}, ${airport.country})`.toLowerCase();
          return fullName.includes(searchTerm.toLowerCase());
      });
  }

  // Handle changes to the departure airport search term
  function handleDepartureSearchChange(event) {
      searchTermDeparture = event.target.value;
  }

  // Handle changes to the destination airport search term
  function handleDestinationSearchChange(event) {
      searchTermDestination = event.target.value;
  }

  // Handle changes to the departure airport selection
  function handleDepartureChange(event) {
      departure_airport = event.target.value;
  }

  // Handle changes to the destination airport selection
  function handleDestinationChange(event) {
      destination_airport = event.target.value;
  }

  function handleNumberPeopleChange(event) {
      number_of_people = event.target.value;
  }

  function handleBudgetChange(event) {
      budgetRange = [event.target.value[0], event.target.value[1]];
  }

  function handleDepartureDateChange(event) {
      departureDate = event.target.value;
  }

  function handleReturnDateChange(event) {
      returnDate = event.target.value;
  }

  function handleCityDestinationChange(event) {
    destination_city = event.target.value;
  }

  async function generate(event) {
    const travelData = {
        departure_airport,
        destination_airport,
        number_of_people,
        budget_range: 3000, // temp hard coding budget
        departure_date: departureDate,
        return_date: returnDate,
        city_destination: destination_city
    };

    try {
        const response = await fetch("http://127.0.0.1:5000/api/travel", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(travelData)
        });

        if (!response.ok) {
            throw new Error("Network response was not ok");
        }

        const result = await response.json();
        apiResponse = result.details;  // Store the result details
        displayApiResponse();  // Update UI with the received data
    } catch (error) {
        console.error("There was a problem with the API request:", error);
    }
  }

  // Display the API response data in the UI
  function displayApiResponse() {
    const responseContainer = document.getElementById("responseContainer");

    // Check if apiResponse is defined, log it for debugging
    if (!apiResponse) {
        console.error("apiResponse is undefined");
        return;
    }
    console.log("apiResponse:", apiResponse);

    // Safely access best hotels and activities with default values
    let hotelsHtml = "";
    if (Array.isArray(apiResponse.best_hotels)) {
        hotelsHtml = apiResponse.best_hotels.map(hotel => {
            const [name, price, url] = hotel; 
            return `
                <div class="hotel">
                    <h4>${name}</h4>
                    <p>Price: ${price}</p>
                    <a href="${url}" target="_blank">Book Now</a>
                </div>
            `;
        }).join("");
    } else {
        hotelsHtml = "<p>No hotels available</p>";
    }

    let activitiesHtml = ""
    if (Array.isArray(apiResponse.activities)) {
      activitiesHtml = apiResponse.activities.map(activ =>{
        const [name, address, description] = activ;
        return `
                <div class="hotel">
                    <h4>${name}</h4>
                    <p>Price: ${address}</p>
                    <a href="${description}" target="_blank">Book Now</a>
                </div>
            `;
        }).join("");
    } else {
        activitiesHtml= "<p>No hotels available</p>";
    }

    // Set up the innerHTML with AI response check and default values
    responseContainer.innerHTML = `
        <h2>Your Travel Plan</h2>
        
        <div>
            <h3>Best Hotels</h3>
            ${hotelsHtml}
        </div>
        
        <div>
            <h3>Activities</h3>
            ${activitiesHtml}
        </div>

        <md-block>
            <strong>AI Response:</strong>
            <div>${apiResponse.openai_response || "No response available"}</div>
        </md-block>
        
        <p><strong>Total Flight Price:</strong> ${apiResponse.total_flight_price || "N/A"}</p>
    `;

    // Re-initialize the md-block after setting innerHTML
    const mdBlockScript = document.createElement('script');
    mdBlockScript.src = 'https://md-block.verou.me/md-block.js';
    mdBlockScript.type = 'module';
    mdBlockScript.onload = () => {
        console.log('md-block script reloaded and applied.');
    };
    document.head.appendChild(mdBlockScript);
}


  // Run fetchAirports function when the script loads
  fetchAirports();
</script>

<main>
  <h1>Travel Details</h1>

  <!-- Departure Airport Search Input -->
  <label>
      Departure Airport:
      <input
          type="text"
          placeholder="Search for Departure Airport"
          value="{searchTermDeparture}"
          on:input="{handleDepartureSearchChange}"
      />
      <select on:change="{handleDepartureChange}" bind:value="{departure_airport}">
          <option value="">Select Departure Airport</option>
          {#each filteredAirports(searchTermDeparture) as airport}
              <option value="{airport.code}">{airport.name} ({airport.city}, {airport.country})</option>
          {/each}
      </select>
  </label>

  <!-- Destination Airport Search Input -->
  <label>
      Destination Airport:
      <input
          type="text"
          placeholder="Search for Destination Airport"
          value="{searchTermDestination}"
          on:input="{handleDestinationSearchChange}"
      />
      <select on:change="{handleDestinationChange}" bind:value="{destination_airport}">
          <option value="">Select Destination Airport</option>
          {#each filteredAirports(searchTermDestination) as airport}
              <option value="{airport.code}">{airport.name} ({airport.city}, {airport.country})</option>
          {/each}
      </select>
  </label>

  <!-- Number of People Input -->
  <label>
      Number of People:
      <input
          type="number"
          placeholder="Number of People"
          on:input="{handleNumberPeopleChange}"
          bind:value="{number_of_people}"
      />
  </label>

  <label>
    Destination city:
    <input
        type="text"
        placeholder="Destination City"
        on:input="{handleCityDestinationChange}"
        bind:value="{destination_city}"
    />
  </label>

  <!-- Budget Range Input -->
  <label>
      Budget Range:
      <input
          type="range"
          min="{budgetRange[0]}"
          max="{budgetRange[1]}"
          bind:value="{budgetRange}"
          on:input="{handleBudgetChange}"
      />
      <span>Left: {budgetRange[0]}</span> - <span>Right: {budgetRange[1]}</span>
  </label>

  <!-- Departure Date Input -->
  <label>
      Departure Date:
      <input
          type="date"
          on:input="{handleDepartureDateChange}"
          bind:value="{departureDate}"
      />
  </label>

  <!-- Return Date Input -->
  <label>
      Return Date:
      <input
          type="date"
          on:input="{handleReturnDateChange}"
          bind:value="{returnDate}"
      />
  </label>

  <label>
    <button  on:click="{generate}" >Ask your personalized AI travel agent </button>
  </label>

  <!-- Container to display the API response -->
  <div id="responseContainer"></div>
</main>


