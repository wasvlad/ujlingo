const ENDPOINTS = {
  "random-words":     "/api/teaching/random/words/init_test",
  "new-words":        "/api/teaching/tests/words/new",
  "weak-words":       "/api/teaching/tests/words/weak-knowledge",
  "strong-words":     "/api/teaching/tests/words/strong-knowledge",
  "new-sentences":    "/api/teaching/tests/sentences/new",
  "weak-sentences":   "/api/teaching/tests/sentences/weak-knowledge",
  "strong-sentences": "/api/teaching/tests/sentences/strong-knowledge"
};

document.addEventListener("DOMContentLoaded", () => {
  const select         = document.getElementById("test-select");
  const startTestBtn   = document.getElementById("start-test-btn");
  const customInput    = document.getElementById("custom-sentence-input");
  const startCustomBtn = document.getElementById("start-custom-test-btn");

  select.addEventListener("change", () => {
    startTestBtn.disabled = !select.value;
  });

  customInput.addEventListener("input", () => {
    startCustomBtn.disabled = customInput.value.trim().length === 0;
  });

  startTestBtn.addEventListener("click", () => {
    const key = select.value;
    if (!key) return;
    window.location.href = `/html/test.html?test=${encodeURIComponent(key)}`;
  });

  startCustomBtn.addEventListener("click", async () => {
    const sentence = customInput.value.trim();
    if (!sentence) return;

    try {
      const resp = await fetch("/api/teaching/custom_sentence_test", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sentence })
      });
      const data = await resp.json();
      console.log("Init custom response:", resp.status, data);

      if (resp.ok) {
        localStorage.setItem("customSentence", sentence);
        localStorage.setItem("currentTestKey", "custom");
        window.location.href = `/html/test.html?test=custom`;
      } else {
        alert(data.detail || `Error: ${resp.status}`);
      }
    } catch (err) {
      console.error("Custom test init error:", err);
      alert("Network error while starting custom test.");
    }
  });
});
