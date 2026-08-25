const startButton = document.getElementById("start-button");
const howToPlayButton = document.getElementById("how-to-play-button");
const tutorialButton = document.getElementById("tutorial-button");

console.log("Cidade antes:");
console.log(cidade);

construirEscola();

console.log("Cidade depois:");
console.log(cidade);

if (startButton) {
    startButton.addEventListener("click", () => {
        window.location.href = "./city.html";
    });
}

if (howToPlayButton) {
    howToPlayButton.addEventListener("click", () => {
        window.location.href = "./how-to-play.html";
    });
}

if (tutorialButton) {
    tutorialButton.addEventListener("click", () => {
        window.location.href = "./index.html";
    });
}