const INIT_ENDPOINTS = {
  "random-words":     "/api/teaching/random/words/init_test",
  "new-words":        "/api/teaching/tests/words/new",
  "weak-words":       "/api/teaching/tests/words/weak-knowledge",
  "strong-words":     "/api/teaching/tests/words/strong-knowledge",
  "new-sentences":    "/api/teaching/tests/sentences/new",
  "weak-sentences":   "/api/teaching/tests/sentences/weak-knowledge",
  "strong-sentences": "/api/teaching/tests/sentences/strong-knowledge",
  "custom":           "/api/teaching/custom_sentence_test"
};

function getTestKey() {
  const params = new URLSearchParams(window.location.search);
  return params.get("test");
}

function humanizeKey(key) {
  return key.replace(/-/g, " ");
}

let initialized = false;

async function doInit() {
  if (initialized) return;

  const key = getTestKey();
  const storedKey = localStorage.getItem("currentTestKey");

  if (storedKey && storedKey === key) {
    initialized = true;
    return;
  }

  if (storedKey && storedKey !== key) {
    throw new Error("Already running");
  }

  const endpoint = INIT_ENDPOINTS[key];
  if (!endpoint) throw new Error("Unknown test: " + key);

  let fetchOptions = {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" }
  };

  if (key === "custom") {
    const sentence = localStorage.getItem("customSentence");
    if (!sentence) {
      throw new Error("No custom sentence stored");
    }
    fetchOptions.body = JSON.stringify({ sentence });
  }

  const resp = await fetch(endpoint, fetchOptions);
  let data;
  try {
    data = await resp.json();
  } catch (_) {
    data = {};
  }
  console.log("Init response:", resp.status, data);

  if (resp.ok) {
    initialized = true;
    localStorage.setItem("currentTestKey", key);
    return;
  }

  if (data.detail === "Test session is already initialized") {
    if (storedKey === key) {
      initialized = true;
      return;
    } else {
      throw new Error("Already running");
    }
  }

  if (data.detail === "No questions") {
    throw new Error("No questions");
  }

  throw new Error(data.detail || `Init failed (status ${resp.status})`);
}

function buildSentence(tokens) {
  return tokens.reduce((sentence, token, i) => {
    if (i === 0) return token;
    return /^[.,!?;:]$/.test(token) ? sentence + token : sentence + " " + token;
  }, "");
}

async function loadQuestion() {
  const qText     = document.getElementById("question-text");
  const formGroup = document.querySelector(".form-group");
  const submitBtn = document.getElementById("submit-answer-btn");
  const finishBtn = document.getElementById("test-finished-btn");

  try {
    await doInit();
  } catch (initErr) {
    const storedKey = localStorage.getItem("currentTestKey");
    if (initErr.message === "No questions") {
      const [prefix, suffix] = getTestKey().split("-");
      qText.textContent = `Before going to ${prefix} ${suffix} you should try new ${suffix}.`;
    } else if (initErr.message === "Already running") {
      const activeKey   = storedKey || getTestKey();
      const humanActive = humanizeKey(activeKey);
      qText.textContent = `You should complete ${humanActive} test before starting another.`;
    } else {
      console.error("Init error:", initErr);
      qText.textContent = "Error initializing test";
    }
    formGroup.style.display = "none";
    submitBtn.style.display = "none";
    finishBtn.style.display = "block";
    return;
  }

  try {
    const res = await fetch("/api/teaching/get_question", {
      method: "GET",
      credentials: "include"
    });
    const data = await res.json();

    if (!res.ok || data.message === "Test is finished") {
      qText.textContent = data.message || "Test is finished";
      formGroup.style.display = "none";
      submitBtn.style.display = "none";
      finishBtn.style.display = "block";
      localStorage.removeItem("currentTestKey");
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

    if (data.type === 1) {
      items.forEach(token => {
        const btn = document.createElement("button");
        btn.type        = "button";
        btn.className   = "token-btn";
        btn.textContent = token;

        btn.addEventListener("click", () => {
          const prev = container.querySelector(".token-btn.selected");
          if (prev && prev !== btn) {
            prev.classList.remove("selected");
          }
          btn.classList.add("selected");
          answerInput.value = token;
          selectedDiv.textContent = `Chosen: ${token}`;
        });

        container.appendChild(btn);
      });
    } else {
      let selectedTokens = [];

      items.forEach(token => {
        const btn = document.createElement("button");
        btn.type        = "button";
        btn.className   = "token-btn";
        btn.textContent = token;

        btn.addEventListener("click", () => {
          const idx = selectedTokens.indexOf(token);
          if (idx === -1) {
            selectedTokens.push(token);
            btn.classList.add("selected");
          } else {
            selectedTokens.splice(idx, 1);
            btn.classList.remove("selected");
          }
          const sentence = buildSentence(selectedTokens);
          answerInput.value = sentence;
          selectedDiv.textContent = sentence
            ? `Built sentence: ${sentence}`
            : "";
        });

        container.appendChild(btn);
      });
    }
  } catch (err) {
    console.error("Load question error:", err);
    qText.textContent = "Error loading question";
    formGroup.style.display = "none";
    submitBtn.style.display = "none";
    finishBtn.style.display = "none";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadQuestion();

  document.getElementById("answer-form").addEventListener("submit", async e => {
    e.preventDefault();
    const messageEl = document.getElementById("response-message");
    const rawAnswer = document.getElementById("answer-input")?.value.trim();

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
