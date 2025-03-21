const message = document.getElementById('message');

const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');
const notice = urlParams.get('notice');

if (notice === 'success') {
  message.textContent = "Registration completed successfully. Please check your email inbox and click the activation link.";
  message.style.color = 'green';
} else if (token) {
  fetch(`/api/user/confirm_email?token=${encodeURIComponent(token)}`)
    .then(async response => {
      const result = await response.json();

      if (response.ok) {
        message.textContent = result.message || "E-mail has been successfully confirmed.";
        message.style.color = 'green';
      } else {
        message.textContent = result.detail || "E-mail confirmation failed.";
        message.style.color = 'red';
      }
    })
    .catch(error => {
      console.error("Connection error:", error);
      message.textContent = "Connection to the server failed.";
      message.style.color = 'red';
    });
} else {
  message.textContent = "Invalid access to the page.";
  message.style.color = 'red';
}
