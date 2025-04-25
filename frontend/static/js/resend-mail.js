document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('resend-form');
  const emailInput = document.getElementById('email');
  const statusMsg = document.getElementById('status-message');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim();

    if (!email) {
      statusMsg.textContent = 'Please enter your e-mail.';
      statusMsg.style.color = 'red';
      return;
    }

    try {
      const response = await fetch('/api/user/resend-verification-link', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      const data = await response.json();

      if (response.ok) {
        window.location.href = '/html/confirm_email.html?notice=resend-success';
      } else {
        statusMsg.textContent = data.detail || 'Something went wrong.';
        statusMsg.style.color = 'red';
      }
    } catch (err) {
      statusMsg.textContent = 'Failed to connect to the server.';
      statusMsg.style.color = 'red';
    }
  });
});
