function submitRegistration(data) {
  const message = document.getElementById('message');

  fetch('/api/user/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json; charset=UTF-8'
    },
    body: JSON.stringify(data)
  })
    .then(response => response.json().then(result => ({ response, result })))
    .then(({ response, result }) => {
      if (response.ok) {
        window.location.href = "confirm_email.html?notice=success";
      } else {
        if (result.detail && typeof result.detail === "string") {
          message.textContent = result.detail;
        } else if (Array.isArray(result.detail)) {
          const messages = result.detail.map(err => {
            const field = err?.loc?.[1] || '';
            const msg = err?.msg || '';
            return `${field}: ${msg}`;
          });
          message.textContent = messages.join(" | ");
        } else {
          message.textContent = 'Error occurred during registration';
        }
        message.style.color = 'red';
      }
    })
    .catch(error => {
      console.error("Connection error:", error);
      message.textContent = 'Backend connection failed';
      message.style.color = 'red';
    });
}
