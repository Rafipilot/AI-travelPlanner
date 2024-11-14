<script>
  import Rounter from "svelte-spa-router"
  import input_page from "./routes/input_page.svelte"
  import landing_page from "./routes/landing_page.svelte"




//test
  let routes = {
    "/":  landing_page,
    "/input_page": input_page,
  }
</script>

<main>
  <Rounter {routes}/>
</main>