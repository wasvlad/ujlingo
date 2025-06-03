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
  const select = document.getElementById("test-select");
  const btn    = document.getElementById("start-test-btn");

  select.addEventListener("change", () => {
    btn.disabled = !select.value;
  });

  btn.addEventListener("click", () => {
    const key = select.value;
    if (!key) return;
    window.location.href = `/html/test.html?test=${encodeURIComponent(key)}`;
  });
});
