const languageSelect = document.getElementById("language");
const difficultySelect = document.getElementById("difficulty");
const loadButton = document.getElementById("load-text");
const finishButton = document.getElementById("finish-session");

const practiceText = document.getElementById("practice-text");
const input = document.getElementById("typing-input");

const wpmElement = document.getElementById("wpm");
const accuracyElement = document.getElementById("accuracy");
const timeElement = document.getElementById("time");
const message = document.getElementById("practice-message");

let currentTextId = null;
let startTime = null;
let timerId = null;

function calculateLiveStats() {
  if (!startTime) return;

  const seconds = (Date.now() - startTime) / 1000;
  const typed = input.value;
  const target = practiceText.textContent;

  const words = target.trim().split(/\s+/).length;
  const wpm = seconds > 0 ? Math.round(words / (seconds / 60)) : 0;

  let correct = 0;

  for (let i = 0; i < typed.length; i++) {
    if (typed[i] === target[i]) correct++;
  }

  const accuracy = typed.length ? Math.round((correct / typed.length) * 100) : 0;

  wpmElement.textContent = wpm;
  accuracyElement.textContent = `${accuracy}%`;
  timeElement.textContent = `${Math.floor(seconds)} c`;
}

input.addEventListener("input", () => {
  if (!startTime) {
    startTime = Date.now();
    timerId = setInterval(calculateLiveStats, 200);
  }

  calculateLiveStats();
});

loadButton.addEventListener("click", async () => {
  message.textContent = "";

  const language = languageSelect.value;
  const difficulty = difficultySelect.value;

  const params = new URLSearchParams({ language });

  if (difficulty) {
    params.set("difficulty", difficulty);
  }

  const response = await fetch(`/texts/random?${params}`);

  if (!response.ok) {
    message.textContent = "Не удалось загрузить текст.";
    return;
  }

  const data = await response.json();

  currentTextId = data.id;
  practiceText.textContent = data.content;

  input.value = "";
  input.disabled = false;
  finishButton.disabled = false;

  startTime = null;
  clearInterval(timerId);

  wpmElement.textContent = "0";
  accuracyElement.textContent = "0%";
  timeElement.textContent = "0 c";
});

finishButton.addEventListener("click", async () => {
  if (!currentTextId || !startTime) return;

  clearInterval(timerId);

  const duration = (Date.now() - startTime) / 1000;

  const response = await fetch("/sessions/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${localStorage.getItem("access_token")}`,
    },
    body: JSON.stringify({
      text_id: currentTextId,
      typed_text: input.value,
      duration_seconds: duration,
    }),
  });

  if (!response.ok) {
    message.textContent = "Не удалось сохранить результат.";
    return;
  }

  const result = await response.json();

  wpmElement.textContent = result.wpm;
  accuracyElement.textContent = `${result.accuracy}%`;
  timeElement.textContent = `${Math.round(result.duration_seconds)} c`;

  input.disabled = true;
  finishButton.disabled = true;
  message.textContent = "Результат сохранён.";
});