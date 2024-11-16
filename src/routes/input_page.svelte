

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
  let budget = 100;
  let departureDate = "";
  let returnDate = "";
  let airports = [];  // Array to store airport data
  let searchTermDeparture = "";  // Search term for departure airport
  let searchTermDestination = "";  // Search term for destination airport
  let destination_city = "";
  let apiResponse = null;  // Variable to store API response data
  let isLoading = false; 

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
        hide_departure_dropdown('departureDropdown'); // Hide the dropdown after selection
    }

    // Handle changes to the destination airport selection
    function handleDestinationChange(event) {
        destination_airport = event.target.value;
        hide_destination_dropdown("destinationDropdown")
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

    function handleCityDestinationChange(event) {
    destination_city = event.target.value;
    }

    function show_destination_dropdown(dropdownId) {
        const dropdown = document.getElementById(dropdownId);
        if (dropdown) {
            console.log(`Showing dropdown for: ${dropdownId}`);
            dropdown.style.display = "block";
        } else {
            console.log(`Dropdown not found for: ${dropdownId}`);
        }
}

    function hide_destination_dropdown(dropdownId) {
        const dropdown = document.getElementById(dropdownId);
        if (dropdown){
            dropdown.style.display = "none" // hide      
        }
    }


  function show_departure_dropdown(dropdownId)  {
    const dropdown = document.getElementById(dropdownId)
    if (dropdown) {
        dropdown.style.display = "block" // show
    }
}

    function hide_departure_dropdown(dropdownId){
        const dropdown = document.getElementById(dropdownId);
        if (dropdown) {
            dropdown.style.display = "none" // hide 
        }
    }
  function showSection(sectionId) {
    // Hide all sections initially
    document.getElementById("hotelsSection").style.display = "none";
    document.getElementById("activitiesSection").style.display = "none";
    document.getElementById("aiResponseSection").style.display = "none";

    // Show the selected section
    document.getElementById(sectionId + "Section").style.display = "block";
}


async function generate(event) {
    const travelData = {
      departure_airport,
      destination_airport,
      number_of_people,
      budget_range: Number(budget),
      departure_date: departureDate,
      return_date: returnDate,
      city_destination: destination_city
    };

    isLoading = true; // Start showing the spinner
    try {
      const response = await fetch("https://my-svelte-project.onrender.com/api/travel", {
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
      displayApiResponse(); 
    } catch (error) {
      console.error("API request error:", error);
    } finally {
      isLoading = false; // Stop showing the spinner
    }
  }



  // Display the API response data in the UI
  function displayApiResponse() {
    document.getElementById("mainPage").style.display = "none";
    document.getElementById("responsePage").style.display = "block";

    // Populate hotels section
    let hotelsHtml = "";
    if (Array.isArray(apiResponse.best_hotels)) {
        hotelsHtml = apiResponse.best_hotels.map(hotel => {
            const [name, price, url] = hotel;
            return `
                <div class="hotel">
                    <h4>${name}</h4>
                    <p>Price: ${price}$ (Per night)</p>
                    <a href="${url}" target="_blank">Book Now</a>
                </div>
            `;
        }).join("");
    } else {
        hotelsHtml = "<p>No hotels available</p>";
    }
    document.getElementById("hotelsContent").innerHTML = hotelsHtml;

    // Populate activities section
    let activitiesHtml = "";
    if (Array.isArray(apiResponse.activities)) {
        activitiesHtml = apiResponse.activities.map(activ => {
            const [name, address, description] = activ;
            return `
                <div class="activity">
                    <h4>${name}</h4>
                    <p>Address: ${address}</p>
                    <p>Description: ${description}</p>
                </div>
            `;
        }).join("");
    } else {
        activitiesHtml = "<p>No activities available</p>";
    }
    document.getElementById("activitiesContent").innerHTML = activitiesHtml;

    // Populate AI response section using md-block for Markdown rendering
    document.getElementById("aiResponseContent").innerHTML = `
        <md-block>
            <strong>AI Response:</strong>
            ${apiResponse.openai_response || "No response available"}
        </md-block>
    `;

    // Reinitialize md-block to render Markdown
    const mdBlockScript = document.createElement('script');
    mdBlockScript.src = 'https://md-block.verou.me/md-block.js';
    mdBlockScript.type = 'module';
    mdBlockScript.onload = () => {
        console.log('md-block script reloaded and applied for Markdown rendering.');
    };
    document.head.appendChild(mdBlockScript);
}




  // Run fetchAirports function when the script loads
  fetchAirports();
</script>



<main>
    <div id = "mainPage">
  <h1>Travel Details</h1>

  <!-- Departure Airport Search Input -->
  <label>
    Departure Airport:
    <input
        type="text"
        placeholder="Search for Departure Airport"
        value="{searchTermDeparture}"
        on:input="{handleDepartureSearchChange}"
        on:focus="{() => show_departure_dropdown('departureDropdown')}" 
    />
    <select
        id="departureDropdown"
        on:change="{handleDepartureChange}" 
        bind:value="{departure_airport}"
        size="{filteredAirports(searchTermDeparture).length || 1}" 
        style="display: none;" 
    >
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
    on:focus="{() => show_destination_dropdown('destinationDropdown')}"
/>
<select
    id="destinationDropdown"
    on:change="{handleDestinationChange}"
    bind:value="{destination_airport}"
    size="{filteredAirports(searchTermDestination).length || 1}"
    style="display: none;"
>
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
    Budget:
    <input
      type="range"
      min="100"
      max="20000"
      step="10"
      on:input="{handleBudgetChange}"
    />
    <span>{budget}</span>
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
    <button on:click="{generate}" id="start_button">Ask your personalized AI travel agent</button>
  </label>
</div>

{#if isLoading}
  <!-- Spinner Container -->
  <div class="spinner"></div>
{/if}

  <!-- Container to display the API response -->
  <div id="responsePage" style="display: none;">
    <!-- Display API Response here -->

        <!-- Tab links -->
        <div id="tab">
            <button on:click="{() => showSection('hotels')}" id="tab_buttons">Best Hotels</button>
            <button on:click="{() => showSection('activities')}" id="tab_buttons">Activities</button>
            <button on:click="{() => showSection('aiResponse')}" id="tab_buttons">AI Response</button>
        </div>
     
        <!-- Tab content sections -->
        <div id="hotelsSection" class="tabContent" style="display: none;">
            <h3>Best Hotels</h3>
            <div id="hotelsContent"></div> <!-- Dynamic content goes here -->
        </div>
     
        <div id="activitiesSection" class="tabContent" style="display: none;">
            <h3>Activities</h3>
            <div id="activitiesContent"></div> <!-- Dynamic content goes here -->
        </div>
     
        <div id="aiResponseSection" class="tabContent" style="display: none;">
            <h3>AI Response</h3>
            <div id="aiResponseContent"></div> <!-- Dynamic content goes here -->
        </div>
     
        <!-- Back button to return to main input page -->
     
 </div>
</main>


