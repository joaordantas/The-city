const prefeitoAtual = document.getElementById("prefeito-atual");
const indicadoresTopo = document.getElementById("indicadores-topo");
const painelEconomia = document.getElementById("painel-economia");
const painelTesouraria = document.getElementById("painel-tesouraria");
const painelIndicadores = document.getElementById("painel-indicadores");
const terrenosLivres = document.getElementById("terrenos-livres");
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
    energia: "Energia",
    agua: "Agua",
    poluicao: "Poluicao",
    qualidade_vida: "Qualidade",
    rodada: "Rodada",
};

const temasConstrucoes = {
    casa: "residencial",
    escola: "educacao",
    hospital: "saude",
    parque: "verde",
    comercio: "comercio",
    fabrica: "industria",
    estacao_agua: "agua",
    usina_solar: "energia",
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

function atualizarTela(estado, textoMensagem = "") {
    estadoAtual = estado;
    const cidade = estado.cidade;
    const dados = cidade.dados;

    prefeitoAtual.textContent = cidade.prefeito;
    mensagem.textContent = textoMensagem;

    desenharIndicadoresTopo(dados);
    desenharEconomia(estado.economia);
    desenharBarras(dados);
    desenharMapa(cidade.mapa);
    desenharConstrucoes(estado.construcoes_disponiveis);
    desenharEvento(cidade.evento_ativo);
    desenharHistorico(cidade.historico);
    verificarFimDeJogo(cidade);
}

function desenharIndicadoresTopo(dados) {
    const itens = [
        ["dinheiro", formatarDinheiro(dados.dinheiro), "saldo"],
        ["populacao", dados.populacao, "habitantes"],
        ["empregos", dados.empregos, "vagas"],
        ["educacao", `${dados.educacao}/100`, "ensino"],
        ["saude", `${dados.saude}/100`, "saude"],
        ["qualidade_vida", `${dados.qualidade_vida}/100`, "bem-estar"],
        ["rodada", `${dados.rodada}/${dados.max_rodadas}`, "rodada"],
    ];

    indicadoresTopo.innerHTML = itens
        .map(([chave, valor, detalhe]) => `
            <article class="indicador-topo indicador-${chave}">
                <span>${nomesIndicadores[chave]}</span>
                <strong>${valor}</strong>
                <small>${detalhe}</small>
            </article>
        `)
        .join("");
}

function desenharEconomia(economia) {
    painelEconomia.innerHTML = [
        ["Receitas", formatarDinheiro(economia.receitas), "positivo"],
        ["Despesas", formatarDinheiro(economia.despesas), "negativo"],
        ["Lucro / prejuizo", formatarDinheiro(economia.resultado), economia.resultado >= 0 ? "positivo" : "negativo"],
        ["Atividade economica", formatarDinheiro(economia.atividade_economica), ""],
        ["Trabalhadores", economia.trabalhadores, ""],
        ["Desempregados", economia.desempregados, ""],
    ]
        .map(([nome, valor, classe]) => `<dt>${nome}</dt><dd class="${classe}">${valor}</dd>`)
        .join("");

    painelTesouraria.innerHTML = [
        ["Manutencao", formatarDinheiro(economia.manutencao)],
        ["Servicos publicos", formatarDinheiro(economia.servicos_publicos)],
        ["Resultado previsto", formatarDinheiro(economia.resultado)],
    ]
        .map(([nome, valor]) => `<dt>${nome}</dt><dd>${valor}</dd>`)
        .join("");
}

function desenharBarras(dados) {
    const chaves = ["energia", "agua", "poluicao", "educacao", "saude", "qualidade_vida"];
    painelIndicadores.innerHTML = chaves
        .map((chave) => `
            <div class="barra-item">
                <div>
                    <span>${nomesIndicadores[chave]}</span>
                    <strong>${dados[chave]} / 100</strong>
                </div>
                <meter min="0" max="100" value="${dados[chave]}"></meter>
            </div>
        `)
        .join("");
}

function desenharMapa(lotes) {
    const construcoesPorId = Object.fromEntries(
        estadoAtual.construcoes_disponiveis.map((construcao) => [construcao.id, construcao])
    );

    const livres = lotes.filter((lote) => lote === null).length;
    terrenosLivres.textContent = `${livres} / ${lotes.length}`;

    mapa.innerHTML = lotes
        .map((construcaoId) => {
            const construcao = construcoesPorId[construcaoId];
            const tema = temasConstrucoes[construcaoId] || "vazio";
            const titulo = construcao ? construcao.nome : "Terreno livre";
            const texto = construcao ? construcao.nome : "Livre";
            return `
                <button class="lote lote-${tema} ${construcao ? "ocupado" : ""}" title="${titulo}">
                    <span class="predio"></span>
                    <strong>${texto}</strong>
                </button>
            `;
        })
        .join("");
}

function desenharConstrucoes(construcoes) {
    listaConstrucoes.innerHTML = construcoes
        .map((construcao) => `
            <article class="card-construcao card-${temasConstrucoes[construcao.id] || "vazio"}">
                <div>
                    <strong>${construcao.nome}</strong>
                    <small>Custo ${formatarDinheiro(construcao.custo)} | Manutencao ${formatarDinheiro(construcao.manutencao)}</small>
                </div>
                <p>${construcao.descricao}</p>
                <button type="button" data-construcao="${construcao.id}">Construir</button>
            </article>
        `)
        .join("");
}

function desenharEvento(evento) {
    if (!evento) {
        eventoAtivo.innerHTML = "<strong>Cidade estavel</strong><p>Nenhum evento ativo nesta rodada.</p>";
        return;
    }

    eventoAtivo.innerHTML = `<strong>${evento.titulo}</strong><p>${evento.descricao}</p>`;
}

function desenharHistorico(itens) {
    historico.innerHTML = itens.map((item) => `<li>${item}</li>`).join("");
}

function verificarFimDeJogo(cidade) {
    if (cidade.status === "falencia") {
        mensagem.textContent = "Falencia municipal. A cidade ficou muitas rodadas no vermelho.";
        botaoRodada.disabled = true;
    } else if (cidade.status === "concluido") {
        mensagem.textContent = "Fim do MVP. Compare seus indicadores finais.";
        botaoRodada.disabled = true;
    } else {
        botaoRodada.disabled = false;
    }
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

async function iniciarJogo() {
    const parametros = new URLSearchParams(window.location.search);
    const prefeito = (parametros.get("prefeito") || "").trim();
    const estado = await chamarApi("/api/novo-jogo", { prefeito });
    atualizarTela(estado, "Escolha uma construcao ou avance a rodada.");
}

botaoRodada.addEventListener("click", avancarRodada);

listaConstrucoes.addEventListener("click", (evento) => {
    const botao = evento.target.closest("[data-construcao]");
    if (botao) {
        construir(botao.dataset.construcao);
    }
});

iniciarJogo();
