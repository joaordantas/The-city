const CHAVE_ANIMACOES = "the-city-animacoes";

export class CidadeViva {
    constructor(canvas, checkbox) {
        this.canvas = canvas;
        this.contexto = canvas.getContext("2d");
        this.ativo = localStorage.getItem(CHAVE_ANIMACOES) !== "off";
        this.quadro = null;
        this.fase = 0;
        this.intensidade = 1;
        checkbox.checked = this.ativo;
        checkbox.addEventListener("change", () => {
            this.ativo = checkbox.checked;
            localStorage.setItem(CHAVE_ANIMACOES, this.ativo ? "on" : "off");
            this.atualizar();
        });
        new ResizeObserver(() => this.redimensionar()).observe(canvas.parentElement);
        this.redimensionar();
    }

    definirCidade(estado) {
        this.intensidade = Math.min(1.8, 0.5 + estado.cidade.dados.populacao / 200);
        this.atualizar();
    }

    redimensionar() {
        const caixa = this.canvas.getBoundingClientRect();
        const escala = Math.min(devicePixelRatio || 1, 2);
        this.canvas.width = Math.max(1, Math.round(caixa.width * escala));
        this.canvas.height = Math.max(1, Math.round(caixa.height * escala));
        this.contexto.setTransform(escala, 0, 0, escala, 0, 0);
    }

    atualizar() {
        if (!this.ativo || document.hidden) {
            cancelAnimationFrame(this.quadro);
            this.quadro = null;
            this.contexto.clearRect(0, 0, this.canvas.width, this.canvas.height);
            return;
        }
        if (!this.quadro) this.animar();
    }

    animar() {
        const largura = this.canvas.clientWidth;
        const altura = this.canvas.clientHeight;
        this.contexto.clearRect(0, 0, largura, altura);
        this.fase = (this.fase + 0.45 * this.intensidade) % (largura + 50);
        this.contexto.fillStyle = "#ffd54f";
        for (let i = 0; i < 3; i += 1) {
            const x = (this.fase + i * largura / 3) % Math.max(largura, 1);
            const y = altura - 24 - (i % 2) * 8;
            this.contexto.fillRect(x, y, 12, 6);
            this.contexto.fillStyle = "#163b55";
            this.contexto.fillRect(x + 2, y + 6, 3, 3);
            this.contexto.fillRect(x + 8, y + 6, 3, 3);
            this.contexto.fillStyle = "#ffd54f";
        }
        this.contexto.fillStyle = "#244e62";
        for (let i = 0; i < 5; i += 1) {
            const x = (largura - this.fase * 0.35 + i * 83) % Math.max(largura, 1);
            const y = 22 + (i % 3) * 10;
            this.contexto.beginPath();
            this.contexto.arc(x, y, 2.5, 0, Math.PI * 2);
            this.contexto.fill();
            this.contexto.fillRect(x - 1, y + 3, 2, 6);
        }
        this.quadro = requestAnimationFrame(() => this.animar());
    }

    destruir() {
        cancelAnimationFrame(this.quadro);
    }
}
