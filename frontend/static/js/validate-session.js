async function checkSession() {
  try {
    const response = await fetch('/api/user/validate-session', {
      method: 'GET',
      credentials: 'include'
    });

    if (response.ok) {
      const data = await response.json();
      const welcome = document.getElementById('welcome');
      if (welcome) welcome.innerText = data.message;
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

async function updateSessionMessageLinks() {
  const loginLink = document.getElementById('login-session-link');
  const registerLink = document.getElementById('register-session-link');

  try {
    const response = await fetch('/api/user/validate-session', {
      method: 'GET',
      credentials: 'include'
    });

    if (response.ok) {
      if (loginLink) {
        loginLink.innerHTML = `
          You are already logged in
          <a class="clickable-link" href="/html/main.html">Click here</a>
        `;
      }

      if (registerLink) {
        registerLink.innerHTML = `
          You are already logged in
          <a class="clickable-link" href="/html/main.html">Click here</a>
        `;
      }

    } else {
      const result = await response.json();

      if (loginLink) {
        loginLink.innerHTML = `
          Don't have an account?
          <a class="clickable-link" href="/html/register.html">Create an account</a>
        `;
      }

      if (registerLink) {
        registerLink.innerHTML = `
          Already have an account?
          <a class="clickable-link" href="/html/login.html">Sign in</a>
        `;
      }
    }
  } catch (error) {
    console.error("Session link rendering error:", error);

    if (loginLink) {
      loginLink.innerHTML = `
        Don't have an account?
        <a class="clickable-link" href="/html/register.html">Create an account</a>
      `;
    }

    if (registerLink) {
      registerLink.innerHTML = `
        Already have an account?
        <a class="clickable-link" href="/html/login.html">Sign in</a>
      `;
    }
  }
}