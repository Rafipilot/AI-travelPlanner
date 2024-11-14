<script>
  let destination_airport = "";
  let departure_airport = "";
  let number_of_people = 0;
  let budgetRange = [100, 20000];
  let departureDate = "";
  let returnDate = "";
  let airports = [];  // Array to store airport data
  let searchTermDeparture = "";  // Search term for departure airport
  let searchTermDestination = "";  // Search term for destina;ion airport
  let destination_city = "";

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
        budget_range: 3000,
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
        console.log("API Response:", result);
    } catch (error) {
        console.error("There was a problem with the API request:", error);
    }
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
        type="str"
        placeholder="Destionation City"
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

    <button on:click="{generate}">Ask your perosnalised AI travel agent</button>
  </label>
</main>

<style>
  /* Example styles, customize as needed */
  label {
      display: block;
      margin-bottom: 1em;
  }

  input, select {
      display: block;
      margin-top: 0.5em;
  }

  input[type="text"] {
      width: 100%;
      padding: 8px;
  }
</style>
