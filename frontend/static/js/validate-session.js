async function checkSession() {
  try {
    const response = await fetch('/api/user/validate-session', {
      method: 'GET',
      credentials: 'same-origin'
    });

    if (response.ok) {
      const data = await response.json();
      document.getElementById('welcome').innerText = data.message;
    } else {
      const result = await response.json();
      if (result.detail === "Email is not confirmed") {
        window.location.href = '/html/login.html?notice=unconfirmed';
      } else {
        window.location.href = '/html/login.html';
      }
    }
  } catch (error) {
    console.error('Error during session validation:', error);
    window.location.href = '/html/login.html';
  }
}