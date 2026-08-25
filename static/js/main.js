const telaInicial = document.getElementById("tela-inicial");
const telaJogo = document.getElementById("tela-jogo");
const formInicio = document.getElementById("form-inicio");
const inputPrefeito = document.getElementById("nome-prefeito");
const prefeitoAtual = document.getElementById("prefeito-atual");
const indicadoresTopo = document.getElementById("indicadores-topo");
const painelEconomia = document.getElementById("painel-economia");
const mapa = document.getElementById("mapa");
const listaConstrucoes = document.getElementById("lista-construcoes");
const eventoAtivo = document.getElementById("evento-ativo");
const historico = document.getElementById("historico");
const mensagem = document.getElementById("mensagem");
const botaoRodada = document.getElementById("botao-rodada");

let estadoAtual = null;

const nomesIndicadores = {
    dinheiro: "Dinheiro",
    populacao: "Populacao",
    empregos: "Empregos",
    educacao: "Educacao",
    saude: "Saude",
    qualidade_vida: "Qualidade",
    rodada: "Rodada",
};

function formatarDinheiro(valor) {
    return `R$ ${Number(valor).toLocaleString("pt-BR")}`;
}

async function chamarApi(url, dados = null) {
    const opcoes = dados
        ? {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(dados),
          }
        : {};

    const resposta = await fetch(url, opcoes);
    return resposta.json();
}

function mostrarJogo() {
    telaInicial.classList.add("escondido");
    telaJogo.classList.remove("escondido");
}

function atualizarTela(estado, textoMensagem = "") {
    estadoAtual = estado;
    const cidade = estado.cidade;
    const dados = cidade.dados;

    prefeitoAtual.textContent = cidade.prefeito;
    mensagem.textContent = textoMensagem;

    desenharIndicadores(dados);
    desenharEconomia(estado.economia);
    desenharMapa(cidade.mapa);
    desenharConstrucoes(estado.construcoes_disponiveis);
    desenharEvento(cidade.evento_ativo);
    desenharHistorico(cidade.historico);
    verificarFimDeJogo(cidade);
}

function desenharIndicadores(dados) {
    const chaves = ["dinheiro", "populacao", "empregos", "educacao", "saude", "qualidade_vida", "rodada"];

    indicadoresTopo.innerHTML = chaves
        .map((chave) => {
            const valor = chave === "dinheiro" ? formatarDinheiro(dados[chave]) : dados[chave];
            return `
                <div class="indicador">
                    <span>${nomesIndicadores[chave]}</span>
                    <strong>${valor}</strong>
                </div>
            `;
        })
        .join("");
}

function desenharEconomia(economia) {
    const itens = [
        ["Receitas", formatarDinheiro(economia.receitas)],
        ["Despesas", formatarDinheiro(economia.despesas)],
        ["Resultado previsto", formatarDinheiro(economia.resultado)],
        ["Atividade economica", formatarDinheiro(economia.atividade_economica)],
        ["Trabalhadores", economia.trabalhadores],
        ["Desempregados", economia.desempregados],
    ];

    painelEconomia.innerHTML = itens
        .map(([nome, valor]) => `<dt>${nome}</dt><dd>${valor}</dd>`)
        .join("");
}

function desenharMapa(lotes) {
    const construcoesPorId = Object.fromEntries(
        estadoAtual.construcoes_disponiveis.map((construcao) => [construcao.id, construcao])
    );

    mapa.innerHTML = lotes
        .map((construcaoId, indice) => {
            const construcao = construcoesPorId[construcaoId];
            const conteudo = construcao ? construcao.emoji : "+";
            const titulo = construcao ? construcao.nome : "Lote vazio";
            return `<button class="lote ${construcao ? "ocupado" : ""}" data-posicao="${indice}" title="${titulo}">${conteudo}</button>`;
        })
        .join("");
}

function desenharConstrucoes(construcoes) {
    listaConstrucoes.innerHTML = construcoes
        .map(
            (construcao) => `
                <article class="card-construcao">
                    <strong>${construcao.emoji} ${construcao.nome}</strong>
                    <small>Custo: ${formatarDinheiro(construcao.custo)} | Manutencao: ${formatarDinheiro(construcao.manutencao)}</small>
                    <p>${construcao.descricao}</p>
                    <button type="button" data-construcao="${construcao.id}">Construir</button>
                </article>
            `
        )
        .join("");
}

function desenharEvento(evento) {
    if (!evento) {
        eventoAtivo.innerHTML = "<strong>Nenhum evento ativo.</strong><p>A cidade esta estavel nesta rodada.</p>";
        return;
    }

    eventoAtivo.innerHTML = `<strong>${evento.titulo}</strong><p>${evento.descricao}</p>`;
}

function desenharHistorico(itens) {
    historico.innerHTML = itens.map((item) => `<li>${item}</li>`).join("");
}

function verificarFimDeJogo(cidade) {
    telaJogo.classList.toggle("fim-jogo", cidade.status !== "jogando");

    if (cidade.status === "falencia") {
        mensagem.textContent = "A cidade entrou em falencia municipal. Tente equilibrar melhor as despesas.";
        botaoRodada.disabled = true;
    } else if (cidade.status === "concluido") {
        mensagem.textContent = "Voce chegou ao fim das rodadas do MVP. Agora compare seus indicadores finais.";
        botaoRodada.disabled = true;
    } else {
        botaoRodada.disabled = false;
    }
}

async function iniciarJogo(evento) {
    evento.preventDefault();
    const prefeito = inputPrefeito.value.trim() || "Prefeito";
    const estado = await chamarApi("/api/novo-jogo", { prefeito });
    mostrarJogo();
    atualizarTela(estado, "Cidade iniciada. Escolha uma construcao ou avance a rodada.");
}

async function construir(construcaoId) {
    const posicaoLivre = estadoAtual.cidade.mapa.findIndex((lote) => lote === null);
    const resposta = await chamarApi("/api/construir", {
        construcao_id: construcaoId,
        posicao: posicaoLivre,
    });
    atualizarTela(resposta, resposta.mensagem);
}

async function avancarRodada() {
    const resposta = await chamarApi("/api/proxima-rodada", {});
    atualizarTela(resposta, resposta.mensagem);
}

formInicio.addEventListener("submit", iniciarJogo);
botaoRodada.addEventListener("click", avancarRodada);

listaConstrucoes.addEventListener("click", (evento) => {
    const botao = evento.target.closest("[data-construcao]");
    if (!botao) {
        return;
    }

    construir(botao.dataset.construcao);
});

