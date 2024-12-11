<script>
  import { user } from './store';
  import axios from 'axios';
  import { onMount } from 'svelte';
  
  let email = '';
  let password = '';
  let message = '';
  let isLoggedIn = false;

  const registerUser = async () => {
    try {
      const response = await axios.post('http://localhost:5000/register', {
        email,
        password
      });
      message = response.data.message;
    } catch (error) {
      message = error.response.data.error;
    }
  };

  const loginUser = async () => {
    try {
      const response = await axios.post('http://localhost:5000/login', {
        email,
        password
      });
      message = response.data.message;
      user.set(response.data);  // Set the user data in the store
      isLoggedIn = true;
    } catch (error) {
      message = error.response.data.error;
    }
  };
</script>

<main>
  {#if !isLoggedIn}
    <h1>Login / Register</h1>
    <input bind:value={email} placeholder="Email" type="email" />
    <input bind:value={password} placeholder="Password" type="password" />
    <button on:click={loginUser}>Login</button>
    <button on:click={registerUser}>Register</button>
    <p>{message}</p>
  {:else}
    <h1>Hi {email}</h1>
  {/if}
</main>

<style>
  main {
    text-align: center;
    margin-top: 50px;
  }

  input {
    margin: 5px;
    padding: 10px;
  }

  button {
    padding: 10px;
    margin: 10px;
  }
</style>
