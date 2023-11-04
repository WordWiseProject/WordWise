const showButton = document.getElementById("showButton");
const nextButton = document.getElementById("nextButton");
const card = document.getElementById("card");
let isFlipped = false;
let word = document.getElementById("word");

document.addEventListener("DOMContentLoaded", function () {
  const card = document.getElementById("card");
  const showButton = document.getElementById("showButton");
  const nextButton = document.getElementById("nextButton");
  const backButton = document.getElementById("backButton");
  const wordElement = document.querySelector(".text-6xl");
  const pronunciationElement = document.querySelector(".text-black.ml-2");
  const meaningElement = document.querySelector(".text-black.ml-1");

  const wordData = [
    {
      word: "Adorable",
      pronunciation: "/əˈdɔːr.ə.bəl/",
      meaning: "inspiring great affection; delightful; charming.",
    },
      {
        word: "Adventurous",
        pronunciation: "/ədˈven.tʃər.əs/",
        meaning: "willing to try new or difficult things, or exciting and often dangerous.",
      }


    // Add more word data objects as needed
  ];

  let currentIndex = 0;

  function showCardSide(side) {
    card.classList.remove("flipped");
    if (side === "back") {
      card.classList.add("flipped");
    }
  }

  function showFront() {
    showCardSide("front");
  }

  function showBack() {
    showCardSide("back");
  }

  function showNextCard() {
    currentIndex = (currentIndex + 1) % wordData.length;
    showFront();
    updateCard();
  }

  function showPreviousCard() {
    currentIndex = (currentIndex - 1 + wordData.length) % wordData.length;
    showFront();
    updateCard();
  }

  function updateCard() {
    const word = wordData[currentIndex];
    wordElement.textContent = word.word;
    pronunciationElement.textContent = word.pronunciation;
    meaningElement.textContent = `(adj.) ${word.meaning}`;
  }

  showFront();

  showButton.addEventListener("click", showBack);
  nextButton.addEventListener("click", showNextCard);
  backButton.addEventListener("click", showPreviousCard);
});
