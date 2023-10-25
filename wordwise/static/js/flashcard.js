const showButton = document.getElementById("showButton");
const backButton = document.getElementById("backButton");
const card = document.getElementById("card");
let isFlipped = false;

showButton.addEventListener("click", () => {
    if (!isFlipped) {
        card.style.transform = "rotateY(180deg)";
        card.querySelector(".card-front").style.display = "none";
        card.querySelector(".card-back").style.display = "block";
        isFlipped = true;
    }
});

backButton.addEventListener("click", () => {
    if (isFlipped) {
        card.style.transform = "rotateY(0deg)";
        card.querySelector(".card-front").style.display = "block";
        card.querySelector(".card-back").style.display = "none";
        isFlipped = false;
    }
});
