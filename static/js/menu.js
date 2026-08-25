function enviarInicio(evento) {
    evento.preventDefault();
    const inputPrefeito = document.getElementById("nome-prefeito");
    const prefeito = inputPrefeito.value.trim() || "Prefeito";
    const destino = `/jogo?prefeito=${encodeURIComponent(prefeito)}`;
    window.location.href = destino;
}

function abrirTutorial() {
    const modalTutorial = document.getElementById("modal-tutorial");
    modalTutorial.classList.remove("escondido");
    modalTutorial.setAttribute("aria-hidden", "false");
}

function fecharTutorial() {
    const modalTutorial = document.getElementById("modal-tutorial");
    modalTutorial.classList.add("escondido");
    modalTutorial.setAttribute("aria-hidden", "true");
}
