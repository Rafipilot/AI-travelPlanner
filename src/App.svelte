<script>
  import Rounter from "svelte-spa-router"
  import input_page from "./routes/input_page.svelte"
  import landing_page from "./routes/landing_page.svelte"
  import about from "./routes/about.svelte"
  import blog from "./routes/blog.svelte"
  import login from "./routes/login.svelte"
  import Dashboard from "./routes/dashboard.svelte"
  import create from "./routes/create-user.svelte"



//test
  let routes = {
    "/":  login,
    "/input_page": input_page,
    "/create-user": create,
    "/about_page": about,
    "/blog_page": blog,
    "/dashboard": Dashboard
  }
</script>

<main>
  <Rounter {routes}/>
</main>