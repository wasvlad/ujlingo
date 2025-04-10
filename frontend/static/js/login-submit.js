function submitLogin(data) {
  const message = document.getElementById('message');

  fetch('/api/user/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json; charset=UTF-8'
    },
    credentials: 'include',
    body: JSON.stringify(data)
  })
    .then(res => res.json().then(result => ({ response: res, result })))
    .then(async ({ response, result }) => {
      if (response.ok) {
        message.textContent = result.message || 'Login successful';
        message.style.color = 'green';
        try {
          const adminCheck = await fetch('/api/admin/validate-session', {
            method: 'GET',
            credentials: 'include'
          });

          if (adminCheck.ok) {
            window.location.href = '/html/admin-panel.html';
            return;
          }
        } catch (e) {
          console.error('Admin check failed:', e);
        }

        setTimeout(() => {
          window.location.href = '/html/main.html';
        }, 1000);
      } else {
        message.textContent = result.detail || 'Invalid email or password';
        message.style.color = 'red';
      }
    })
    .catch(error => {
      console.error("Connection error:", error);
      message.textContent = 'Cannot connect with server';
      message.style.color = 'red';
    });
}
