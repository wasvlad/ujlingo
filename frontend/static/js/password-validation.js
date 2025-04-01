export function setupLivePasswordValidation(passwordInputId) {
  const passwordInput = document.getElementById(passwordInputId);
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
}

function toggleRequirement(element, condition) {
  element.style.color = condition ? 'green' : 'red';
  const icon = element.querySelector('img');
  if (icon) {
    icon.src = condition
      ? '../static/images/valid.png'
      : '../static/images/invalid.png';
  }
}

export function isPasswordStrong(password) {
  return (
    /[A-Z]/.test(password) &&
    /[a-z]/.test(password) &&
    /\d/.test(password) &&
    /[!@#$%^&*(),.?":{}|<>]/.test(password) &&
    password.length >= 8
  );
}
