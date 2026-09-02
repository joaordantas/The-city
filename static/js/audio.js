const CHAVE_SONS = "the-city-sons";

export class AudioJogo {
    constructor(checkbox) {
        this.contexto = null;
        this.ativo = localStorage.getItem(CHAVE_SONS) !== "off";
        checkbox.checked = this.ativo;
        checkbox.addEventListener("change", () => {
            this.ativo = checkbox.checked;
            localStorage.setItem(CHAVE_SONS, this.ativo ? "on" : "off");
            this.tocar("confirmar");
        });
    }

    tocar(tipo = "acao") {
        if (!this.ativo) return;
        this.contexto ||= new AudioContext();
        const oscilador = this.contexto.createOscillator();
        const ganho = this.contexto.createGain();
        const frequencias = { acao: 440, confirmar: 620, erro: 180, rodada: 520 };
        oscilador.frequency.value = frequencias[tipo] || frequencias.acao;
        ganho.gain.setValueAtTime(0.035, this.contexto.currentTime);
        ganho.gain.exponentialRampToValueAtTime(0.001, this.contexto.currentTime + 0.12);
        oscilador.connect(ganho).connect(this.contexto.destination);
        oscilador.start();
        oscilador.stop(this.contexto.currentTime + 0.12);
    }
}
