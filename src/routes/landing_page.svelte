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
  <a href="/#/input_page" id="links">Get Started</a>
  <!-- Use <md-block> here after loading the script -->
  <md-block>## Header</md-block>
</main>
