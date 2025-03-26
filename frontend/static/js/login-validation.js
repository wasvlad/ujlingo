const form = document.getElementById('login-form');
const message = document.getElementById('message');

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  message.textContent = '';
  let valid = true;

  const email = form.email.value.trim();
  const password = form.password.value;

  const inputs = form.querySelectorAll('input');
  inputs.forEach(input => input.classList.remove('error-border'));

  if (!email || !password) {
    message.textContent = 'Please fill out all fields';
    message.style.color = 'red';
    if (!email) form.email.classList.add('error-border');
    if (!password) form.password.classList.add('error-border');
    return;
  }

  const emailPattern = /^[^@]+@[^@]+\.[^@]+$/;
  if (!emailPattern.test(email)) {
    form.email.classList.add('error-border');
    message.textContent = 'Email address is not valid';
    message.style.color = 'red';
    return;
  }

  if (password.length < 8) {
    form.password.classList.add('error-border');
    message.textContent = 'Password must be at least 8 characters';
    message.style.color = 'red';
    return;
  }

  submitLogin({ email, password });
});
