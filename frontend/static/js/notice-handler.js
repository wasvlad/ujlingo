document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const notice = urlParams.get('notice');
  const message = document.getElementById('message');
  const resendMail = document.getElementById('resend-mail-link');

  if (!message) return;

  if (notice === 'unconfirmed' && resendMail) {
    resendMail.style.display = 'block';
    message.textContent = 'Please confirm your e-mail before logging in';
    message.style.color = 'red';
  }

  if (notice === 'password-reset-success') {
    message.textContent = 'Password reset successful\n Sign in using your new password';
    message.style.color = 'green';
  }
});
