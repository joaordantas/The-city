import assert from "node:assert/strict";

const intervalos = new Set();
globalThis.window = {
    setInterval(callback) {
        intervalos.add(callback);
        return callback;
    },
    clearInterval(callback) {
        intervalos.delete(callback);
    },
};

const { ControladorRodadas } = await import("../static/js/rodadas.js");

let agora = 1_000_000;
let encerramentos = 0;
let ultimaAtualizacao = null;
const controlador = new ControladorRodadas({
    config: {
        duracoes: [
            { inicio: 1, fim: 2, tempo: 60 },
            { inicio: 3, fim: 5, tempo: 60 },
            { inicio: 6, fim: 10, tempo: 55 },
            { inicio: 11, fim: 15, tempo: 50 },
            { inicio: 16, fim: 20, tempo: 45 },
        ],
    },
    relogio: () => agora,
    aoAtualizar: (estado) => { ultimaAtualizacao = estado; },
    aoEncerrar: async () => { encerramentos += 1; },
});

assert.deepEqual(
    [1, 3, 6, 11, 16].map((rodada) => controlador.obterDuracao(rodada)),
    [60, 60, 55, 50, 45]
);

controlador.iniciar(1, 20);
assert.equal(intervalos.size, 1, "deve existir somente um intervalo");
agora += 15_000;
controlador.sincronizar();
assert.equal(ultimaAtualizacao.segundos, 45, "deve descontar tempo real pelo relogio");

assert.equal(controlador.pausar(), true);
const restantePausado = ultimaAtualizacao.segundos;
agora += 15_000;
controlador.sincronizar();
assert.equal(ultimaAtualizacao.segundos, restantePausado, "tempo pausado nao deve mudar");
assert.equal(controlador.retomar(), true);
assert.equal(intervalos.size, 1, "retomar nao deve duplicar intervalos");
agora += 5_000;
controlador.sincronizar();
assert.equal(ultimaAtualizacao.segundos, restantePausado - 5);

agora += 60_000;
controlador.sincronizar();
controlador.sincronizar();
await Promise.resolve();
assert.equal(encerramentos, 1, "o zero deve processar a rodada uma unica vez");
assert.equal(ultimaAtualizacao.segundos, 0);

controlador.parar();
assert.equal(intervalos.size, 0);
console.log("Timer, drift, pausa, retomada e encerramento unico validados.");
