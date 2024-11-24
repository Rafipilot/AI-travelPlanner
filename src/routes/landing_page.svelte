<script>
  let showMoreInfo = false;

  function toggleInfo() {
    showMoreInfo = !showMoreInfo;
  }
</script>

<svelte:head>
  <title>Travex | AI Travel Planner - Plan Your Dream Vacation</title>
  <meta
    name="description"
    content="Plan your dream vacation in minutes with Travex. Our AI-powered tool personalizes travel plans, flights, hotels, and activities for a seamless experience."
  />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://travex.world/" />
  <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebApplication",
      "name": "Travex",
      "url": "https://travex.world",
      "description": "Plan your dream vacation in minutes with Travex. AI-powered travel plans tailored to you.",
      "applicationCategory": "Travel",
      "operatingSystem": "All",
      "offers": {
        "@type": "Offer",
        "price": "0.00",
        "priceCurrency": "USD",
        "availability": "https://schema.org/InStock"
      }
    }
  </script>
</svelte:head>

<main id="landing_page">
  <header>
    <h1>Travex</h1>
    <p id="sub-title">Plan your dream vacation in minutes</p>
  </header>

    <a href="/#/input_page" id="start_button">Get Started</a>
    <button class="info-toggle" on:click={toggleInfo}>
      {showMoreInfo ? "Hide Details" : "Learn More"}
    </button>

    {#if showMoreInfo}
      <p class="more-info">
        Travex uses cutting-edge AI to craft personalized travel plans based on your preferences. 
        Discover flights, hotels, restaurants, and activities all in one place, then watch as it 
        weaves them into a seamless itinerary. Your next adventure is just a few clicks away!
      </p>
    {/if}

</main>