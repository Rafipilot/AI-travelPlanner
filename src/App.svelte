<script>
  import Rounter from "svelte-spa-router"
  import input_page from "./routes/input_page.svelte"
  import landing_page from "./routes/landing_page.svelte"
  import about from "./routes/about.svelte"



//test
  let routes = {
    "/":  landing_page,
    "/input_page": input_page,
    "/about_page": about,
  }
</script>

<main>
  <Rounter {routes}/>
</main>