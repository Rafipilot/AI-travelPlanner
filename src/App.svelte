<script>
  import Rounter from "svelte-spa-router"

  import login from "./routes/main.svelte"
  import main from "./routes/main.svelte"
  import about from "./routes/about.svelte"
  import blog from "./routes/blog.svelte"
  import landing from "./routes/landing.svelte"

  let routes = {
    "/":  landing,
    "/dashboard": main,
    "/about_page": about,
    "/blog_page": blog,
  }
</script>

<main>
  <Rounter {routes}/>
</main>