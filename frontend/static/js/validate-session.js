async function checkSession() {
  const loginLink = document.getElementById('login-session-link');
  const registerLink = document.getElementById('register-session-link');
  const welcome = document.getElementById('welcome');

  try {
    const response = await fetch('/api/user/validate-session', {
      method: 'GET',
      credentials: 'include'
    });

    if (response.ok) {
      const data = await response.json();

      if (welcome) {
        welcome.innerText = data.message;
      }

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

      if (result.detail === "Email is not confirmed") {
          window.location.href = '/html/login.html?notice=unconfirmed';
          return;
      }

      if (loginLink || registerLink) {
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
  } else {
    window.location.href = '/html/login.html';
  }
}
  } catch (error) {
    console.error('Error during session validation:', error);

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

    if (!loginLink && !registerLink && !welcome) {
      window.location.href = '/html/login.html';
    }
  }
}
