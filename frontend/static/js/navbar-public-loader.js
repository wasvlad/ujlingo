document.addEventListener("DOMContentLoaded", () => {
  fetch("/static/components/navbar-public.html")
    .then(response => {
      if (!response.ok) throw new Error("Failed to load navbar");
      return response.text();
    })
    .then(html => {
      const container = document.createElement("div");
      container.innerHTML = html;
      document.body.insertBefore(container, document.body.firstChild);
    })
    .catch(error => console.error("Public navbar loading error:", error));
});
