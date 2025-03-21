const form = document.getElementById('register-form');
const message = document.getElementById('message');

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

  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirm-password').value;

  if (password.length < 8) {
    document.getElementById('password').classList.add('error-border');
    message.textContent = 'Password must be at least 8 characters';
    message.style.color = 'red';
    return;
  }

  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  if (!hasUppercase || !hasLowercase || !hasNumber || !hasSpecialChar) {
    document.getElementById('password').classList.add('error-border');
    message.textContent = 'Password must include uppercase, lowercase, number and special character';
    message.style.color = 'red';
    return;
  }

  if (password !== confirmPassword) {
    document.getElementById('confirm-password').classList.add('error-border');
    message.textContent = 'Passwords don\'t match';
    message.style.color = 'red';
    return;
  }

  // Przekazanie danych do funkcji z innego pliku:
  submitRegistration({
    email,
    password,
    name,
    surname
  });
});
