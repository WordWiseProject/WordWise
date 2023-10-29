const showButton = document.getElementById("showButton");
const nextButton = document.getElementById("nextButton");
const card = document.getElementById("card");
let isFlipped = false;
let word = document.getElementById("word");

showButton.addEventListener("click", () => {
    if (!isFlipped) {
        card.style.transform = "rotateY(180deg)";
        card.querySelector(".card-front").style.display = "none";
        card.querySelector(".card-back").style.display = "block";
        isFlipped = true;
    }
});

nextButton.addEventListener("click", () => {
    if (isFlipped) {
        card.style.transform = "rotateY(0deg)";
        card.querySelector(".card-front").style.display = "block";
        card.querySelector(".card-back").style.display = "none";
        isFlipped = false;
    }
});
