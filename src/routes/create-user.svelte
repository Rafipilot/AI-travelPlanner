<script>
  let username = '';
  let password = '';
  let error = '';
  let successMessage = '';

  const handleSubmit = async () => {
    const response = await fetch('http://127.0.0.1:5000/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      successMessage = 'User registered successfully! You can now log in.';
      username = '';
      password = '';
      error = '';
    } else {
      const data = await response.json();
      error = data.message;
      successMessage = '';
    }
  };
</script>

<main>
  <h1>Create Account</h1>
  {#if error}
    <p style="color: red;">{error}</p>
  {/if}
  {#if successMessage}
    <p style="color: green;">{successMessage}</p>
  {/if}
  <form on:submit|preventDefault={handleSubmit}>
    <label for="username">Username</label>
    <input type="text" id="username" bind:value={username} required />
    
    <label for="password">Password</label>
    <input type="password" id="password" bind:value={password} required />
    
    <button type="submit">Register</button>
  </form>
</main>
