import { setupLivePasswordValidation, isPasswordStrong } from './password-validation.js';

const form = document.getElementById('register-form');
const message = document.getElementById('message');
const passwordInput = document.getElementById('password');

setupLivePasswordValidation('password');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  message.textContent = '';

  const inputs = form.querySelectorAll('input');
  let anyFieldEmpty = false;

  inputs.forEach(input => {
    input.classList.remove('error-border');
    if (!input.value.trim()) {
      input.classList.add('error-border');
      anyFieldEmpty = true;
    }
  });

  if (anyFieldEmpty) {
    message.textContent = 'Please fill out required fields';
    message.style.color = 'red';
    return;
  }

  const email = form.email.value.trim();
  const name = form.name.value.trim();
  const surname = form.surname.value.trim();
  const password = passwordInput.value;
  const confirmPassword = document.getElementById('confirm-password').value;

  if (!/^[^@]+@[^@]+\.[^@]+$/.test(email)) {
    form.email.classList.add('error-border');
    message.textContent = 'Email address is not valid';
    message.style.color = 'red';
    return;
  }

  if (name.length < 2) {
    form.name.classList.add('error-border');
    message.textContent = 'Name must be at least 2 characters long';
    message.style.color = 'red';
    return;
  }

  if (surname.length < 2) {
    form.surname.classList.add('error-border');
    message.textContent = 'Last Name must be at least 2 characters long';
    message.style.color = 'red';
    return;
  }

  if (!isPasswordStrong(password)) {
    message.textContent = 'Password does not meet all the requirements.';
    message.style.color = 'red';
    passwordInput.classList.add('error-border');
    return;
  }

  if (password !== confirmPassword) {
    document.getElementById('confirm-password').classList.add('error-border');
    message.textContent = 'Passwords don\'t match';
    message.style.color = 'red';
    return;
  }

  submitRegistration({ email, password, name, surname });
});
