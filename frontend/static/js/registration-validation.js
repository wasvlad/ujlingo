const form = document.getElementById('register-form');
const message = document.getElementById('message');
const passwordInput = document.getElementById('password');

const reqUppercase = document.getElementById('req-uppercase');
const reqLowercase = document.getElementById('req-lowercase');
const reqNumber = document.getElementById('req-number');
const reqSpecial = document.getElementById('req-special');
const reqLength = document.getElementById('req-length');

passwordInput.addEventListener('input', () => {
  const password = passwordInput.value;
  toggleRequirement(reqUppercase, /[A-Z]/.test(password));
  toggleRequirement(reqLowercase, /[a-z]/.test(password));
  toggleRequirement(reqNumber, /\d/.test(password));
  toggleRequirement(reqSpecial, /[!@#$%^&*(),.?":{}|<>]/.test(password));
  toggleRequirement(reqLength, password.length >= 8);
});

function toggleRequirement(element, condition) {
  element.style.color = condition ? 'green' : 'red';

  const icon = element.querySelector('img');
  if (icon) {
    icon.src = condition
      ? '../static/images/valid.png'
      : '../static/images/invalid.png';
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  let valid = true;
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
  const emailPattern = /^[^@]+@[^@]+\.[^@]+$/;
  if (!emailPattern.test(email)) {
    form.email.classList.add('error-border');
    message.textContent = 'Email address is not valid';
    message.style.color = 'red';
    return;
  }

  const name = form.name.value.trim();
  if (name.length < 2) {
    form.name.classList.add('error-border');
    message.textContent = 'Name must be at least 2 characters long';
    message.style.color = 'red';
    return;
  }

  const surname = form.surname.value.trim();
  if (surname.length < 2) {
    form.surname.classList.add('error-border');
    message.textContent = 'Last Name must be at least 2 characters long';
    message.style.color = 'red';
    return;
  }

  const password = passwordInput.value;
  const confirmPassword = document.getElementById('confirm-password').value;

  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
  const hasValidLength = password.length >= 8;

  if (!hasUppercase || !hasLowercase || !hasNumber || !hasSpecialChar || !hasValidLength) {
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

  submitRegistration({
    email,
    password,
    name,
    surname
  });
});
