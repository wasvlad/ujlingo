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

  btn.addEventListener("click", async () => {
    const key      = select.value;
    const initUrl  = ENDPOINTS[key];
    if (!initUrl) return;

    try {
      await fetch("/api/teaching/end_test", {
        method: "POST", credentials: "include"
      });

      const initRes = await fetch(initUrl, {
        method: "POST", credentials: "include"
      });
      const initData = await initRes.json();
      console.log("Init response:", initRes.status, initData);
      if (!initRes.ok && initData.detail !== "Test session is already initialized") {
        alert("Error initializing test: " + (initData.detail||initRes.status));
        return;
      }

      await new Promise(r => setTimeout(r, 300));
      const checkRes = await fetch("/api/teaching/get_question", {
        method: "GET", credentials: "include"
      });
      const checkData = await checkRes.json();
      console.log("First question check:", checkRes.status, checkData);
      if (!checkRes.ok) {
        alert("Didn't manage to download test: " + (checkData.detail||checkRes.status));
        return;
      }

      window.location.href = `/html/test.html?test=${encodeURIComponent(key)}`;
    } catch (err) {
      console.error("Start test error:", err);
    }
  });
});
