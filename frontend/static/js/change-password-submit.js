import { setupLivePasswordValidation, isPasswordStrong } from './password-validation.js';

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("change-password-form");
  const message = document.getElementById("message");
  const passwordInput = document.getElementById("password");

  setupLivePasswordValidation("password");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const oldPassword = document.getElementById("old-password").value.trim();
    const newPassword = passwordInput.value.trim();
    const confirmPassword = document.getElementById("confirm-password").value.trim();

    if (!isPasswordStrong(newPassword)) {
      message.textContent = "Password does not meet all the requirements.";
      message.style.color = "red";
      passwordInput.classList.add("error-border");
      return;
    }

    if (newPassword !== confirmPassword) {
      document.getElementById("confirm-password").classList.add("error-border");
      message.textContent = "New passwords do not match.";
      message.style.color = "red";
      return;
    }

    try {
      const response = await fetch("/api/user/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
      });

      const result = await response.json();
      message.textContent = result.message || result.detail;

      if (response.ok) {
        message.style.color = "green";
        form.reset();
        setTimeout(() => {
          window.location.href = '/html/main.html';
        }, 1000);
      } else {
        message.style.color = "red";
      }
    } catch (err) {
      console.error("Password change error:", err);
      message.textContent = "An unexpected error occurred.";
      message.style.color = "red";
    }
  });
});
