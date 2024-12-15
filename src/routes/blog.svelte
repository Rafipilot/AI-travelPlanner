<script>
    let posts = [
      {
        id: 1,
        title: "Welcome to the Travex Blog",
        content: "Discover the latest updates, tips, and stories to inspire your travels. Stay tuned for exciting travel guides, itineraries, and much more!",
        date: "December 9, 2024",
      },
      {
        id: 2,
        title: "The Ultimate Travel Planner: How Travex Makes Trip Planning Easy and Personalized",
        content: "Travex is your AI-powered travel assistant, designed to simplify trip planning. Input your destination, budget, and preferences, and let Travex generate a customized itinerary with the best flight, hotel, and activity options. Save time, reduce stress, and enjoy a truly personalized travel experience.",
        date: "December 9, 2024",
      }
    ];
  </script>
  
  <style>
    .post .date {
      color: #888;
      font-size: 0.9rem;
      margin-bottom: 10px;
    }
  </style>
  
  <main id="landing_page">
    <header>
      <h1>Travex Blog</h1>
    </header>
  
    {#each posts as post}
      <article class="post">
        <h2>{post.title}</h2>
        <p class="date">{post.date}</p>
        <p>{post.content}</p>
      </article>
    {/each}
  </main>
  