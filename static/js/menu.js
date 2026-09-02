const configuracoes = document.getElementById("modal-configuracoes");
const creditos = document.getElementById("modal-creditos");
const animacoes = document.getElementById("menu-animacoes");
const sons = document.getElementById("menu-sons");
const formInicio = document.getElementById("form-inicio");

animacoes.checked = localStorage.getItem("the-city-animacoes") !== "off";
sons.checked = localStorage.getItem("the-city-sons") !== "off";
animacoes.addEventListener("change", () => localStorage.setItem("the-city-animacoes", animacoes.checked ? "on" : "off"));
sons.addEventListener("change", () => localStorage.setItem("the-city-sons", sons.checked ? "on" : "off"));
formInicio.addEventListener("submit", () => {
    sessionStorage.removeItem("the-city-partida-ativa");
    sessionStorage.removeItem("the-city-tutorial-concluido");
});

document.addEventListener("click", (evento) => {
    const abrir = evento.target.closest("[data-abrir-menu]");
    if (abrir) {
        const modal = abrir.dataset.abrirMenu === "configuracoes" ? configuracoes : creditos;
        modal.setAttribute("aria-hidden", "false");
        modal.querySelector("button").focus();
    }
    if (evento.target.closest("[data-fechar-menu]")) {
        configuracoes.setAttribute("aria-hidden", "true");
        creditos.setAttribute("aria-hidden", "true");
    }
});

document.addEventListener("keydown", (evento) => {
    if (evento.key === "Escape") {
        configuracoes.setAttribute("aria-hidden", "true");
        creditos.setAttribute("aria-hidden", "true");
    }
});
