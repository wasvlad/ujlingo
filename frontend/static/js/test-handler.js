const INIT_ENDPOINTS = {
  "random-words":     "/api/teaching/random/words/init_test",
  "new-words":        "/api/teaching/tests/words/new",
  "weak-words":       "/api/teaching/tests/words/weak-knowledge",
  "strong-words":     "/api/teaching/tests/words/strong-knowledge",
  "new-sentences":    "/api/teaching/tests/sentences/new",
  "weak-sentences":   "/api/teaching/tests/sentences/weak-knowledge",
  "strong-sentences": "/api/teaching/tests/sentences/strong-knowledge"
};

function getTestKey() {
  const params = new URLSearchParams(window.location.search);
  return params.get("test");
}

let initialized = false;

async function doInit() {
  if (initialized) return;

  const key = getTestKey();
  const endpoint = INIT_ENDPOINTS[key];
  if (!endpoint) {
    throw new Error("Nieznany test: " + key);
  }

  console.log("➤ Initializing test of type:", key, "via", endpoint);
  try {
    const resp = await fetch(endpoint, {
      method: "POST",
      credentials: "include"
    });
    const data = await resp.json();
    console.log("Init response:", resp.status, data);

    if (resp.ok || data.detail === "Test session is already initialized") {
      initialized = true;
      return;
    } else {
      throw new Error(data.detail || `Init failed (status ${resp.status})`);
    }
  } catch (e) {
    console.error("Init error:", e);
    throw e;
  }
}

async function loadQuestion() {
  const qText     = document.getElementById("question-text");
  const formGroup = document.querySelector(".form-group");
  const submitBtn = document.getElementById("submit-answer-btn");
  const finishBtn = document.getElementById("test-finished-btn");

  try {
    await doInit();

    const res = await fetch("/api/teaching/get_question", {
      method: "GET",
      credentials: "include"
    });
    const data = await res.json();
    console.log("GET /get_question →", res.status, data);

    if (!res.ok || data.message === "Test is finished") {
      qText.textContent       = data.message || "Test is finished";
      formGroup.style.display = "none";
      submitBtn.style.display = "none";
      finishBtn.style.display = "block";
      return;
    }

    qText.textContent       = data.question;
    formGroup.innerHTML     = "";
    formGroup.style.display = "";
    submitBtn.style.display = "";

    const oldSel = document.getElementById("selected-container");
    if (oldSel) oldSel.remove();

    if (data.type === 0) {
      formGroup.innerHTML = `
        <input type="text" id="answer-input" name="answer"
               placeholder="Enter your answer" required>
      `;
      return;
    }

    const items = data.type === 1 ? data.options : data.tokens;
    formGroup.innerHTML = `
      <div id="tokens-container" class="tokens"></div>
      <div id="selected-container" class="selected-tokens"></div>
      <input type="hidden" id="answer-input" name="answer" required>
    `;
    const container   = document.getElementById("tokens-container");
    const selectedDiv = document.getElementById("selected-container");
    const answerInput = document.getElementById("answer-input");
    let selected = data.type === 1 ? null : [];

    items.forEach(token => {
      const btn = document.createElement("button");
      btn.type        = "button";
      btn.className   = "token-btn";
      btn.textContent = token;

      btn.addEventListener("click", () => {
        if (data.type === 1) {
          selected = token;
          answerInput.value = token;
          container.querySelectorAll("button").forEach(b => {
            if (b !== btn) b.disabled = true;
          });
          selectedDiv.textContent = `Chosen: ${token}`;
        } else {
          selected.push(token);
          answerInput.value = selected.join(" ");
          btn.disabled = true;
          selectedDiv.textContent = `Built sentence: ${selected.join(" ")}`;
        }
      });

      container.appendChild(btn);
    });

  } catch (err) {
    console.error("Load question error:", err);
    qText.textContent = "Error loading question";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadQuestion();

  document.getElementById("answer-form").addEventListener("submit", async e => {
    e.preventDefault();
    const messageEl = document.getElementById("response-message");
    const rawAnswer = document.getElementById("answer-input").value.trim();

    if (!rawAnswer) {
      messageEl.textContent = "Please enter an answer.";
      messageEl.style.color = "red";
      return;
    }

    try {
      const res    = await fetch("/api/teaching/answer_question", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer: rawAnswer })
      });
      const result = await res.json();
      console.log("POST /answer_question →", res.status, result);

      if (res.ok) {
        if (result.is_correct) {
          messageEl.textContent = "Correct!";
          messageEl.style.color = "green";
        } else {
          messageEl.textContent = `Incorrect. Correct answer: ${result.correct_answer}`;
          messageEl.style.color = "red";
        }
        await loadQuestion();
      } else {
        messageEl.textContent = result.detail || "Failed to submit answer";
        messageEl.style.color = "red";
      }
    } catch (err) {
      console.error("Submit error:", err);
      messageEl.textContent = "Error submitting answer.";
      messageEl.style.color = "red";
    }
  });
});
