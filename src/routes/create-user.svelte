<script>
    import { navigate } from "svelte-routing";
    let username = '';
    let password = '';
    let error = '';
  
    const handleCreateUser = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/create_user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ username, password })
        });
  
        if (response.ok) {
          // Redirect to login after successful user creation
          navigate('/login');
        } else {
          const result = await response.json();
          error = result.message || 'Failed to create user';
        }
      } catch (err) {
        error = 'An error occurred';
      }
    };
  </script>
  
  <main>
    <h2>Create a New User</h2>
    <form on:submit|preventDefault={handleCreateUser}>
      <input type="text" placeholder="Username" bind:value={username} required>
      <input type="password" placeholder="Password" bind:value={password} required>
      <button type="submit">Create User</button>
    </form>
    {#if error}
      <p>{error}</p>
    {/if}
    <p>Already have an account? <a href="/login">Login here</a></p>
  </main>
  