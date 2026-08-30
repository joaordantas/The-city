export class ControladorRodadas {
    constructor({ config, aoAtualizar, aoEncerrar, relogio = () => Date.now() }) {
        this.config = config;
        this.aoAtualizar = aoAtualizar;
        this.aoEncerrar = aoEncerrar;
        this.relogio = relogio;

        this.rodadaAtual = 1;
        this.rodadaMaxima = 1;
        this.tempoTotalRodada = 0;
        this.tempoRestanteMs = 0;
        this.fimRodada = 0;
        this.rodadaAtiva = false;
        this.rodadaProcessando = false;
        this.jogoPausado = false;
        this.intervalo = null;
    }

    obterDuracao(rodada) {
        const faixa = this.config.duracoes.find(
            ({ inicio, fim }) => rodada >= inicio && rodada <= fim
        );

        if (!faixa) {
            throw new Error(`Duracao nao configurada para a rodada ${rodada}.`);
        }

        return faixa.tempo;
    }

    iniciar(rodada, rodadaMaxima) {
        this.pararIntervalo();
        this.rodadaAtual = rodada;
        this.rodadaMaxima = rodadaMaxima;
        this.tempoTotalRodada = this.obterDuracao(rodada);
        this.tempoRestanteMs = this.tempoTotalRodada * 1000;
        this.fimRodada = this.relogio() + this.tempoRestanteMs;
        this.rodadaAtiva = true;
        this.rodadaProcessando = false;
        this.jogoPausado = false;
        this.iniciarIntervalo();
        this.atualizarInterface();
    }

    iniciarIntervalo() {
        this.pararIntervalo();
        this.intervalo = window.setInterval(() => this.sincronizar(), 250);
    }

    pararIntervalo() {
        if (this.intervalo !== null) {
            window.clearInterval(this.intervalo);
            this.intervalo = null;
        }
    }

    sincronizar() {
        if (!this.rodadaAtiva || this.jogoPausado || this.rodadaProcessando) {
            return;
        }

        this.tempoRestanteMs = Math.max(0, this.fimRodada - this.relogio());
        this.atualizarInterface();

        if (this.tempoRestanteMs === 0) {
            this.encerrar("automatico");
        }
    }

    pausar() {
        if (!this.rodadaAtiva || this.rodadaProcessando || this.jogoPausado) {
            return false;
        }

        this.tempoRestanteMs = Math.max(0, this.fimRodada - this.relogio());
        this.jogoPausado = true;
        this.pararIntervalo();
        this.atualizarInterface();
        return true;
    }

    retomar() {
        if (!this.jogoPausado || this.rodadaProcessando) {
            return false;
        }

        this.fimRodada = this.relogio() + this.tempoRestanteMs;
        this.jogoPausado = false;
        this.rodadaAtiva = true;
        this.iniciarIntervalo();
        this.sincronizar();
        return true;
    }

    async encerrar(motivo = "manual") {
        if (!this.rodadaAtiva || this.rodadaProcessando) {
            return false;
        }

        this.rodadaProcessando = true;
        this.rodadaAtiva = false;
        this.jogoPausado = false;
        this.tempoRestanteMs = motivo === "automatico" ? 0 : this.tempoRestanteMs;
        this.pararIntervalo();
        this.atualizarInterface();
        await this.aoEncerrar({ rodada: this.rodadaAtual, motivo });
        return true;
    }

    parar() {
        this.pararIntervalo();
        this.rodadaAtiva = false;
        this.rodadaProcessando = false;
        this.jogoPausado = false;
        this.atualizarInterface();
    }

    atualizarInterface() {
        const segundos = Math.ceil(this.tempoRestanteMs / 1000);
        this.aoAtualizar({
            rodada: this.rodadaAtual,
            rodadaMaxima: this.rodadaMaxima,
            segundos,
            total: this.tempoTotalRodada,
            progresso: this.tempoTotalRodada ? segundos / this.tempoTotalRodada : 0,
            pausado: this.jogoPausado,
            processando: this.rodadaProcessando,
        });
    }
}
