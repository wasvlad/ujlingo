document.addEventListener("DOMContentLoaded", () => {
    fetch("/static/components/navbar.html")
    .then(response => {
      if (!response.ok) throw new Error("Failed to load navbar");
      return response.text();
    })
    .then(html => {
      const container = document.createElement("div");
      container.innerHTML = html;
      document.body.insertBefore(container, document.body.firstChild);

      const logoutBtn = container.querySelector(".logout-btn");
      if (logoutBtn) {
        logoutBtn.addEventListener("click", async () => {
          try {
            const res = await fetch("/api/user/logout", {
              method: "GET",
              credentials: "include"
            });

            if (res.ok) {
              window.location.href = "/";
            } else {
              console.error("Logout failed");
            }
          } catch (err) {
            console.error("Logout error:", err);
          }
        });
      }
    })
    .catch(error => console.error("Navbar loading error:", error));
});