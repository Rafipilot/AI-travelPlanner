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
  
    function showSection(sectionId) {
      // Hide all sections initially
      document.getElementById("hotelsSection").style.display = "none";
      document.getElementById("activitiesSection").style.display = "none";
      document.getElementById("aiResponseSection").style.display = "none";
  
      // Show the selected section
      document.getElementById(sectionId + "Section").style.display = "block";
    }
  
    async function generate(event) {
      console.log("Departure City: ", departure_city, "Destination City: ", destination_city);
      const travelData = {
        departure_city,
        destination_city,
        number_of_people,
        budget_range: Number(budget),
        departure_date: departureDate,
        return_date: returnDate
      };
  
      isLoading = true; // Start showing the spinner
      try {
        const response = await fetch("http://127.0.0.1:5000/api/travel", {
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
  </script>
  
  <main>
    <div id="mainPage">
      <h1>Travel Details</h1>
  
      <!-- Departure City Search Input -->
      <h4>Step 1: Select Departure City</h4>
      <label>
        Departure City:
        <input
          type="text"
          placeholder="Enter Departure City"
          value="{departure_city}"
          on:input="{handleDepartureCityChange}"
        />
      </label>
  
      <!-- Destination City Search Input -->
      <h4>Step 2: Select Destination City</h4>
      <label>
        Destination City:
        <input
          type="text"
          placeholder="Enter Destination City"
          value="{destination_city}"
          on:input="{handleDestinationCityChange}"
        />
      </label>
  
      <!-- Number of People Input -->
      <h4>Step 3: How many people are travelling</h4>
      <label>
        Number of People:
        <input
          type="number"
          placeholder="Number of People"
          on:input="{handleNumberPeopleChange}"
          bind:value="{number_of_people}"
        />
      </label>
  
      <!-- Budget Range Input -->
      <h4>Step 4: What is your budget</h4>
      <label>
        Budget:
        <input
          type="range"
          min="100"
          max="20000"
          step="10"
          on:input="{handleBudgetChange}"
        />
        <span>{budget}$</span>
      </label>
  
      <!-- Departure Date Input -->
      <h4>Step 5: Select your travel dates</h4>
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
          min="{departureDate}"
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
      <div id="tab">
        <button on:click="{() => showSection('hotels')}" id="tab_buttons">Best Hotels</button>
        <button on:click="{() => showSection('activities')}" id="tab_buttons">Activities</button>
        <button on:click="{() => showSection('aiResponse')}" id="tab_buttons">AI Response</button>
      </div>
  
      <div id="hotelsSection" class="tabContent" style="display: none;">
        <h3>Best Hotels</h3>
        <div id="hotelsContent"></div>
      </div>
  
      <div id="activitiesSection" class="tabContent" style="display: none;">
        <h3>Activities</h3>
        <div id="activitiesContent"></div>
      </div>
  
      <div id="aiResponseSection" class="tabContent" style="display: none;">
        <h3>AI Response</h3>
        <div id="aiResponseContent"></div>
      </div>
    </div>
  </main>
  