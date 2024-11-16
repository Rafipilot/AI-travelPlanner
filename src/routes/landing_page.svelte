<script>
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
</script>

<main>
  <h1>CityTravel.AI</h1>
  <p id="sub-title">Plan your dream vaction in minutes</p>
  <a href="/#/input_page" id="start_button">Get Started</a>
</main>
