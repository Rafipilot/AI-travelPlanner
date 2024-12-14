<script>
  import Rounter from "svelte-spa-router"

  import login from "./routes/login.svelte"
  import Dashboard from "./routes/dashboard.svelte"
  import about from "./routes/about.svelte"
  import blog from "./routes/blog.svelte"

  let routes = {
    "/":  login,
    "/dashboard": Dashboard,
    "/about_page": about,
    "/blog_page": blog,
  }
</script>

<main>
  <Rounter {routes}/>
</main>