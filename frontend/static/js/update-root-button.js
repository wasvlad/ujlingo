document.addEventListener("DOMContentLoaded", async () => {
  const container = document.querySelector(".buttons-container");

  if (!container) {
    console.warn("Nie znaleziono .buttons-container – pomijam aktualizację przycisków.");
    return;
  }

  try {
    const response = await fetch("/api/user/validate-session", {
      method: "GET",
      credentials: "include"
    });

    if (response.ok) {
      container.innerHTML = `
        <button class="continue-btn" onclick="window.location.href='/html/main.html'">
          Continue Learning
        </button>
      `;
    } else {
      container.innerHTML = `
        <button class="signin-btn" style="margin-bottom: 20px;" onclick="window.location.href='/html/login.html'">
          Sign In
        </button>
        <button onclick="window.location.href='/html/register.html'">Register</button>
      `;
    }
  } catch (err) {
    console.error("Session check failed:", err);
    container.innerHTML = `
      <button class="signin-btn" style="margin-bottom: 20px;" onclick="window.location.href='/html/login.html'">
        Sign In
      </button>
      <button onclick="window.location.href='/html/register.html'">Register</button>
    `;
  }
});
