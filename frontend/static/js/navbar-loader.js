document.addEventListener("DOMContentLoaded", async () => {
  try {
    const response = await fetch('/api/user/validate-session', {
      method: 'GET',
      credentials: 'include'
    });

    const navbarPath = response.ok
      ? "/static/components/navbar.html"
      : "/static/components/navbar-public.html";

    const navbarRes = await fetch(navbarPath);
    if (!navbarRes.ok) throw new Error("Failed to load navbar");
    const html = await navbarRes.text();

    const container = document.createElement("div");
    container.innerHTML = html;
    document.body.insertBefore(container, document.body.firstChild);

    if (response.ok) {
      const logoutBtn = container.querySelector(".logout-btn");
      if (logoutBtn) {
        logoutBtn.addEventListener("click", async () => {
          try {
            const logoutRes = await fetch("/api/user/logout", {
              method: "GET",
              credentials: "include"
            });

            if (logoutRes.ok) {
              window.location.href = "/";
            } else {
              console.error("Logout failed");
            }
          } catch (err) {
            console.error("Logout error:", err);
          }
        });
      }

      const userIcon = container.querySelector("#user-icon");
      const dropdown = container.querySelector("#user-dropdown");

      if (userIcon && dropdown) {
        userIcon.addEventListener("click", () => {
          dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
        });

        document.addEventListener("click", (e) => {
          if (!userIcon.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = "none";
          }
        });
      }
    }

  } catch (err) {
    console.error("Navbar dynamic loading error:", err);
  }
});
