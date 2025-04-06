const form = document.getElementById("request-reset-form");
const message = document.getElementById("message");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("email").value.trim();

  const emailPattern = /^[^@]+@[^@]+\.[^@]+$/;
  if (!emailPattern.test(email)) {
    form.email.classList.add('error-border');
    message.textContent = "Email address is not valid";
    message.style.color = "red";
    return;
  }

  try {
    const response = await fetch("/api/user/request-password-reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });

    const result = await response.json();
    message.textContent = result.message || result.detail;
    message.style.color = response.ok ? "green" : "red";
  } catch (err) {
    console.error("Reset request error:", err);
    message.textContent = "An unexpected error occurred.";
    message.style.color = "red";
  }
});