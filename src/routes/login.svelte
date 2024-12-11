<script>

    let username = '';
    let password = '';
    let error = '';
  
    const handleLogin = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    });

    console.log(response); // Log response to see what it returns

    if (response.ok) {
      // On successful login, redirect to dashboard
      window.location.href = '/#/dashboard';
    } else {
      const result = await response.json();
      error = result.message || 'Invalid credentials';
    }
  } catch (err) {
    console.error(err); // Log error to understand why it occurred
    error = 'An error occurred';
  }
};

  </script>
  
  <main>
    <h2>Login</h2>
    <form on:submit|preventDefault={handleLogin}>
      <input type="text" placeholder="Username" bind:value={username} required>
      <input type="password" placeholder="Password" bind:value={password} required>
      <button type="submit">Login</button>
    </form>
    {#if error}
      <p>{error}</p>
    {/if}
    <p>Don't have an account? <a href="/#/create-user">Create a new user</a></p>
  </main>
  