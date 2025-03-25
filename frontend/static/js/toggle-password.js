function togglePasswordVisibility(inputId, iconElement) {
  const input = document.getElementById(inputId);
  if (input.type === 'password') {
    input.type = 'text';
    iconElement.src = '../static/images/eye-open.png';
  } else {
    input.type = 'password';
    iconElement.src = '../static/images/eye-closed.png';
  }
}
