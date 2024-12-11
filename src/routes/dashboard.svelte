<script>
    import { onMount } from 'svelte';
  
    let userData = {};
  
    onMount(async () => {
      const response = await fetch('http://127.0.0.1:5000/dashboard', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer ' + localStorage.getItem('authToken'), // Use token or session ID
        },
      });
      if (response.ok) {
        userData = await response.json();
      } 
    });
  </script>
   <main>
    <h2>Welcome {userData.username}</h2>
  </main>

  