document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const notice = urlParams.get('notice');
  const message = document.getElementById('message');

  if (!message) return;

  if (notice === 'unconfirmed') {
    message.textContent = 'Please confirm your e-mail before logging in.';
    message.style.color = 'red';
  }
});
