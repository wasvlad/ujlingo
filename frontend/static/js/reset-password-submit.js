import { setupLivePasswordValidation, isPasswordStrong } from './password-validation.js';

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('reset-password-form');
  const passwordInput = document.getElementById('password');
  const confirmPasswordInput = document.getElementById('confirm-password');
  const message = document.getElementById('message');

  setupLivePasswordValidation('password');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const password = passwordInput.value.trim();
    const confirmPassword = confirmPasswordInput.value.trim();
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    if (!token) {
      message.textContent = 'Invalid or missing token';
      message.style.color = 'red';
      return;
    }

    if (!isPasswordStrong(password)) {
      passwordInput.classList.add('error-border');
      message.textContent = 'Password does not meet all the requirements';
      message.style.color = 'red';
      return;
    }

    if (password !== confirmPassword) {
      confirmPasswordInput.classList.add('error-border');
      message.textContent = 'Passwords do not match';
      message.style.color = 'red';
      return;
    }

    try {
      const res = await fetch(`/api/user/reset-password?token=${encodeURIComponent(token)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ password })
      });

      const result = await res.json();
      message.textContent = result.message || result.detail;
      message.style.color = res.ok ? 'green' : 'red';

      if (res.ok) {
        setTimeout(() => {
          window.location.href = '/html/login.html?notice=password-reset-success';
        }, 1000);
      }

    } catch (err) {
      console.error('Reset password failed:', err);
      message.textContent = 'Unexpected error occurred';
      message.style.color = 'red';
    }
  });
});
