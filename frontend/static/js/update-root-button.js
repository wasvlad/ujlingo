document.addEventListener("DOMContentLoaded", async () => {
  const container = document.querySelector(".buttons-container");

  if (!container) {
    console.warn("Nie znaleziono .buttons-container – pomijam aktualizację przycisków.");
    return;
  }

  try {
    const adminRes = await fetch("/api/admin/validate-session", {
      method: "GET",
      credentials: "include"
    });

    if (adminRes.ok) {
      container.innerHTML = `
        <button class="continue-btn" onclick="window.location.href='/html/admin-panel.html'">
          Continue as Admin
        </button>
      `;
      return;
    }

    const userRes = await fetch("/api/user/validate-session", {
      method: "GET",
      credentials: "include"
    });

    if (userRes.ok) {
      container.innerHTML = `
        <button class="continue-btn" onclick="window.location.href='/html/main.html'">
          Continue Learning
        </button>
      `;
    } else {
      throw new Error("Unauthorized");
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
