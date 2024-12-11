<script>
  import Rounter from "svelte-spa-router"

  import login from "./routes/login.svelte"
  import Dashboard from "./routes/dashboard.svelte"
  import create from "./routes/create-user.svelte"



//test
  let routes = {
    "/":  login,
    "/create-user": create,
    "/dashboard": Dashboard
  }
</script>

<main>
  <Rounter {routes}/>
</main>