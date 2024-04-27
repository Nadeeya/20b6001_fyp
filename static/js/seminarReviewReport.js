// SEMINAR CONTENT
document.addEventListener("DOMContentLoaded", function () {
  const likertForm = document.getElementById("seminar-content");
  const radioButtons = likertForm.querySelectorAll('input[type="radio"]');

  radioButtons.forEach((radio) => {
    radio.addEventListener("change", calculateScore);
  });
});

function calculateScore() {
  const likertForm = document.getElementById("seminar-content");
  const radioButtons = likertForm.querySelectorAll(
    'input[type="radio"]:checked'
  );

  let totalScore = 0;
  radioButtons.forEach((radio) => {
    totalScore += parseInt(radio.value);
  });

  const scoreDisplay = document.getElementById("a_total");
  scoreDisplay.value = totalScore;
}

// QUALITY MANAGEMENT
document.addEventListener("DOMContentLoaded", function () {
  const likertForm = document.getElementById("quality-management");
  const radioButtons = likertForm.querySelectorAll('input[type="radio"]');

  radioButtons.forEach((radio) => {
    radio.addEventListener("change", calculateScore_b);
  });
});

function calculateScore_b() {
  const likertForm = document.getElementById("quality-management");
  const radioButtons = likertForm.querySelectorAll(
    'input[type="radio"]:checked'
  );

  let totalScore = 0;
  radioButtons.forEach((radio) => {
    totalScore += parseInt(radio.value);
  });

  const scoreDisplay = document.getElementById("b_total");
  scoreDisplay.value = totalScore;
}

// COMMUNICATION
document.addEventListener("DOMContentLoaded", function () {
  const likertForm = document.getElementById("communication");
  const radioButtons = likertForm.querySelectorAll('input[type="radio"]');

  radioButtons.forEach((radio) => {
    radio.addEventListener("change", calculateScore_c);
  });
});

function calculateScore_c() {
  const likertForm = document.getElementById("communication");
  const radioButtons = likertForm.querySelectorAll(
    'input[type="radio"]:checked'
  );

  let totalScore = 0;
  radioButtons.forEach((radio) => {
    totalScore += parseInt(radio.value);
  });

  const scoreDisplay = document.getElementById("c_total");
  scoreDisplay.value = totalScore;
}

// OVERALL
document.addEventListener("DOMContentLoaded", function () {
  const likertForm = document.getElementById("overall");
  const radioButtons = likertForm.querySelectorAll('input[type="radio"]');

  radioButtons.forEach((radio) => {
    radio.addEventListener("change", calculateScore_d);
  });
});

function calculateScore_d() {
  const likertForm = document.getElementById("overall");
  const radioButtons = likertForm.querySelectorAll(
    'input[type="radio"]:checked'
  );

  let totalScore = 0;
  radioButtons.forEach((radio) => {
    totalScore += parseInt(radio.value);
  });

  const scoreDisplay = document.getElementById("d_total");
  scoreDisplay.value = totalScore;
}

