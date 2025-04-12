document.addEventListener("DOMContentLoaded", async () => {
  const startBtn = document.getElementById("start-test-btn");

  if (!startBtn) return;

  try {
    const response = await fetch("/api/teaching/random/words/init_test", {
      method: "POST",
      credentials: "include"
    });

    if (response.ok) {
      startBtn.textContent = "Start Test";
      startBtn.addEventListener("click", () => {
        window.location.href = "/html/test.html";
      });
    } else {
      const result = await response.json();
      if (
        result.detail &&
        result.detail === "Test session is already initialized"
      ) {
        startBtn.textContent = "Continue Test";
        startBtn.addEventListener("click", () => {
          window.location.href = "/html/test.html";
        });
      } else {
        alert(result.detail || "Error initializing test");
      }
    }
  } catch (err) {
    console.error("Init test error:", err);
  }
});
