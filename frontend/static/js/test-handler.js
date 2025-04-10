async function loadQuestion() {
  try {
    const res = await fetch("/api/teaching/random/words/get_question", {
      method: "GET",
      credentials: "include"
    });

    const data = await res.json();
    const questionEl = document.getElementById("question-container");

    console.log(data);
    if (res.ok) {
      if (data.message === "Test is finished") {
        questionEl.textContent = data.message;

        document.getElementById("answer-input").style.display = "none";
        document.getElementById("submit-answer-btn").style.display = "none";
        document.getElementById("test-finished-btn").style.display = "block";
} else {
        questionEl.textContent = data.question || "Question loaded";
      }
    } else {
      questionEl.textContent = data.question || "Failed to load question";
    }
  } catch (err) {
    console.error("Load question error:", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadQuestion();

  document.getElementById("submit-answer-btn").addEventListener("click", async () => {
    const answer = document.getElementById("answer-input").value.trim();
    const message = document.getElementById("result-message");

    if (!answer) {
      message.textContent = "Please enter an answer.";
      message.style.color = "red";
      return;
    }

    try {
      const res = await fetch("/api/teaching/random/words/answer_question", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer })
      });

      const result = await res.json();

      if (res.ok) {
        message.textContent = `Correct: ${result.correct}`;
        message.style.color = result.correct ? "green" : "red";
        loadQuestion();
        document.getElementById("answer-input").value = "";
      } else {
        message.textContent = result.detail || "Failed to submit answer";
        message.style.color = "red";
      }
    } catch (err) {
      console.error("Submit answer error:", err);
      message.textContent = "Error submitting answer.";
      message.style.color = "red";
    }
  });
});
