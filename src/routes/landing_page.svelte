<script>
  let showMoreInfo = false;

  function toggleInfo() {
    showMoreInfo = !showMoreInfo;
  }
</script>

<main id="landing_page">
  <h1>Travex</h1>
  <p id="sub-title">Plan your dream vacation in minutes</p>
  <a href="/#/input_page" id="start_button">Get Started</a>
  <button class="info-toggle" on:click={toggleInfo}>
    {showMoreInfo ? "Hide Details" : "Learn More"}
  </button>
  {#if showMoreInfo}
    <p class="more-info">
      Travex uses cutting-edge AI to craft personalized travel plans based on your preferences. 
      Discover flights, hotels, restaurants, and activities all in one place, then watch as 
      it weaves them into a seamless itinerary. Your next adventure is just a few clicks away!
    </p>
  {/if}
</main>
