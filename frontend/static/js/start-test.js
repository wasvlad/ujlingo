document.addEventListener("DOMContentLoaded", () => {
  const startBtn = document.getElementById("start-test-btn");

  if (!startBtn) return;

  startBtn.addEventListener("click", async () => {
    try {
      const response = await fetch("/api/teaching/random/words/init_test", {
        method: "POST",
        credentials: "include"
      });

      if (response.ok) {
        window.location.href = "/html/test.html";
      } else {
        const result = await response.json();
        if (
          result.detail &&
          result.detail === "Test session is already initialized"
        ) {
          window.location.href = "/html/test.html";
        } else {
          alert(result.detail || "Error initializing test");
        }
      }
    } catch (err) {
      console.error("Init test error:", err);
    }
  });
});
