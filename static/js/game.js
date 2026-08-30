import { ControladorRodadas } from "./rodadas.js";

const elementos = {
    prefeitoAtual: document.getElementById("prefeito-atual"),
    nomePrefeitoLateral: document.getElementById("nome-prefeito-lateral"),
    indicadoresTopo: document.getElementById("indicadores-topo"),
    painelEconomia: document.getElementById("painel-economia"),
    painelTesouraria: document.getElementById("painel-tesouraria"),
    previsaoRodada: document.getElementById("previsao-rodada"),
    controlesImpostos: document.getElementById("controles-impostos"),
    painelIndicadores: document.getElementById("painel-indicadores"),
    terrenosLivres: document.getElementById("terrenos-livres"),
    mapa: document.getElementById("mapa"),
    listaConstrucoes: document.getElementById("lista-construcoes"),
    categoriasConstrucoes: document.getElementById("categorias-construcoes"),
    selecaoConstrucao: document.getElementById("selecao-construcao"),
    painelPredio: document.getElementById("painel-predio"),
    eventoAtivo: document.getElementById("evento-ativo"),
    historico: document.getElementById("historico"),
    mensagem: document.getElementById("mensagem"),
    listaAlertas: document.getElementById("lista-alertas"),
    timerCard: document.getElementById("timer-card"),
    numeroRodada: document.getElementById("numero-rodada"),
    tempoRodada: document.getElementById("tempo-rodada"),
    calendarioRodada: document.getElementById("calendario-rodada"),
    progressoTempo: document.getElementById("progresso-tempo"),
    botaoPausa: document.getElementById("botao-pausa"),
    botaoRetomar: document.getElementById("botao-retomar"),
    botaoFinalizar: document.getElementById("botao-finalizar"),
    modalPausa: document.getElementById("modal-pausa"),
    modalConfirmacao: document.getElementById("modal-confirmacao"),
    segundosConfirmacao: document.getElementById("segundos-confirmacao"),
    cancelarFinalizacao: document.getElementById("cancelar-finalizacao"),
    confirmarFinalizacao: document.getElementById("confirmar-finalizacao"),
    painelOperacional: document.getElementById("painel-operacional"),
    tituloPainel: document.getElementById("titulo-painel"),
    fecharPainel: document.getElementById("fechar-painel"),
    overlayTransicao: document.getElementById("overlay-transicao"),
    faseTransicao: document.getElementById("fase-transicao"),
    tituloResumo: document.getElementById("titulo-resumo"),
    itensResumo: document.getElementById("itens-resumo"),
    contagemProxima: document.getElementById("contagem-proxima"),
    modalDemolicao: document.getElementById("modal-demolicao"),
    tituloDemolicao: document.getElementById("titulo-demolicao"),
    reembolsoDemolicao: document.getElementById("reembolso-demolicao"),
    cancelarDemolicao: document.getElementById("cancelar-demolicao"),
    confirmarDemolicao: document.getElementById("confirmar-demolicao"),
};

const paineis = {
    construir: document.getElementById("painel-construir"),
    economia: document.getElementById("painel-economia-conteudo"),
    indicadores: document.getElementById("painel-indicadores-conteudo"),
    eventos: document.getElementById("painel-eventos-conteudo"),
};

const titulosPaineis = {
    construir: "Construir",
    economia: "Economia",
    indicadores: "Indicadores",
    eventos: "Eventos e historico",
};

const nomesIndicadores = {
    energia: "Energia",
    agua: "Agua",
    poluicao: "Poluicao",
    educacao: "Educacao",
    saude: "Saude",
    qualidade_vida: "Qualidade de vida",
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

const meses = [
    "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

let estadoAtual = null;
let controladorRodadas = null;
let painelAberto = null;
let categoriaSelecionada = null;
let construcaoSelecionada = null;
let predioSelecionado = null;
let predioEmMovimento = null;

function formatarDinheiro(valor) {
    return `R$ ${Number(valor).toLocaleString("pt-BR")}`;
}

function formatarTempo(segundos) {
    const minutos = Math.floor(segundos / 60);
    const restante = segundos % 60;
    return `${String(minutos).padStart(2, "0")}:${String(restante).padStart(2, "0")}`;
}

function obterCalendario(rodada) {
    const indice = Math.max(0, rodada - 1);
    return `${meses[indice % 12]} · Ano ${Math.floor(indice / 12) + 1}`;
}

function esperar(milissegundos) {
    return new Promise((resolver) => window.setTimeout(resolver, milissegundos));
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
    const conteudo = await resposta.json();

    if (!resposta.ok) {
        throw new Error(conteudo.mensagem || "Nao foi possivel comunicar com o jogo.");
    }

    return conteudo;
}

function atualizarTela(estado, textoMensagem = "") {
    estadoAtual = estado;
    const cidade = estado.cidade;
    const dados = cidade.dados;

    elementos.prefeitoAtual.textContent = cidade.prefeito;
    elementos.nomePrefeitoLateral.textContent = cidade.prefeito;
    elementos.mensagem.textContent = textoMensagem;
    if (textoMensagem) {
        elementos.mensagem.classList.remove("feedback-acao");
        window.requestAnimationFrame(() => elementos.mensagem.classList.add("feedback-acao"));
    }

    desenharIndicadoresPrincipais(dados);
    desenharEconomia(estado.economia);
    desenharIndicadoresSecundarios(dados, estado.economia);
    desenharMapa(cidade.mapa);
    desenharConstrucoes(estado);
    desenharEvento(cidade.evento_ativo);
    desenharHistorico(cidade.historico);
    desenharAlertas(dados, estado.economia);
    if (predioSelecionado) abrirDetalhesPredio(predioSelecionado);
    atualizarBloqueioAcoes();
}

function desenharIndicadoresPrincipais(dados) {
    const itens = [
        ["Dinheiro", formatarDinheiro(dados.dinheiro), "Saldo disponivel para obras e despesas."],
        ["Populacao", dados.populacao, `Capacidade atual: ${dados.capacidade_populacional} habitantes.`],
        ["Qualidade", `${dados.qualidade_vida}%`, "Resultado combinado de servicos, ambiente e emprego."],
        ["Energia", `${dados.energia}%`, `Capacidade: ${estadoAtual.cidade.simulacao.energia.capacidade}\nDemanda: ${estadoAtual.cidade.simulacao.energia.demanda}`],
        ["Agua", `${dados.agua}%`, `Capacidade: ${estadoAtual.cidade.simulacao.agua.capacidade}\nDemanda: ${estadoAtual.cidade.simulacao.agua.demanda}`],
    ];

    elementos.indicadoresTopo.innerHTML = itens
        .map(([nome, valor, tooltip]) => `
            <article class="indicador-topo" data-tooltip="${tooltip}" tabindex="0">
                <span>${nome}</span>
                <strong>${valor}</strong>
                <small>Atual</small>
            </article>
        `)
        .join("");
}

function desenharEconomia(economia) {
    const ordemReceitas = ["IPTU / Residencial", "Comercio", "Industria", "Outras receitas"];
    const ordemDespesas = ["Saude", "Educacao", "Agua", "Energia", "Infraestrutura", "Outras despesas"];
    elementos.painelEconomia.innerHTML = ordemReceitas
        .map((nome) => [nome, formatarDinheiro(economia.receitas_detalhes[nome]), "positivo"])
        .concat([["Total", formatarDinheiro(economia.receitas), "positivo"]])
        .map(([nome, valor, classe]) => `<dt>${nome}</dt><dd class="${classe}">${valor}</dd>`)
        .join("");
    elementos.painelTesouraria.innerHTML = ordemDespesas
        .map((nome) => `<dt>${nome}</dt><dd class="negativo">-${formatarDinheiro(economia.despesas_detalhes[nome])}</dd>`)
        .concat([`<dt>Total</dt><dd class="negativo">-${formatarDinheiro(economia.despesas)}</dd>`])
        .join("");
    elementos.previsaoRodada.textContent = `${economia.previsao >= 0 ? "+" : "-"}${formatarDinheiro(Math.abs(economia.previsao))}`;
    elementos.previsaoRodada.className = economia.previsao >= 0 ? "positivo" : "negativo";
    const nomes = { residencial: "IPTU", comercio: "Comercio", industria: "Industria" };
    elementos.controlesImpostos.innerHTML = ["residencial", "comercio", "industria"].map((tipo) => {
        const taxa = estadoAtual.cidade.impostos[tipo];
        return `
        <div class="controle-imposto"><span>${nomes[tipo]}</span>
            <button type="button" data-imposto="${tipo}" data-direcao="-1">-</button>
            <strong>${taxa}%</strong>
            <button type="button" data-imposto="${tipo}" data-direcao="1">+</button>
        </div>`;
    }).join("");
}

function criarBarras(chaves, dados) {
    return chaves
        .map((chave) => `
            <div class="barra-item">
                <div><span>${nomesIndicadores[chave]}</span><strong>${dados[chave]}%</strong></div>
                <meter min="0" max="100" value="${dados[chave]}">${dados[chave]}%</meter>
            </div>
        `)
        .join("");
}

function desenharIndicadoresSecundarios(dados, economia) {
    const desemprego = economia.taxa_desemprego;
    const simulacao = estadoAtual.cidade.simulacao;
    const fontesPoluicao = Object.entries(simulacao.poluicao_fontes)
        .map(([nome, valor]) => `<dt>${nome}</dt><dd>${valor >= 0 ? "+" : ""}${valor}</dd>`).join("");

    elementos.painelIndicadores.innerHTML = `
        <section>
            <h3>Cidade</h3>
            <dl class="lista-economia">
                <dt>Populacao</dt><dd>${dados.populacao}</dd>
                <dt>Empregos</dt><dd>${dados.empregos}</dd>
                <dt>Desemprego</dt><dd>${desemprego}%</dd>
            </dl>
        </section>
        <section><h3>Servicos</h3>${criarBarras(["saude", "educacao", "agua", "energia"], dados)}
            <small>Saude ${simulacao.saude.capacidade}/${simulacao.saude.demanda} · Educacao ${simulacao.educacao.capacidade}/${simulacao.educacao.demanda}</small>
            <small>Agua ${simulacao.agua.demanda}/${simulacao.agua.capacidade} · Energia ${simulacao.energia.demanda}/${simulacao.energia.capacidade}</small>
        </section>
        <section><h3>Ambiente</h3>${criarBarras(["poluicao", "qualidade_vida"], dados)}<dl class="lista-economia fontes-poluicao">${fontesPoluicao}</dl></section>
    `;
}

function desenharMapa(lotes) {
    const prediosPorId = Object.fromEntries(estadoAtual.cidade.construcoes.map((predio) => [predio.id, predio]));
    const livres = lotes.filter((lote) => lote === null).length;
    elementos.terrenosLivres.textContent = `${livres} / ${lotes.length}`;
    elementos.mapa.innerHTML = lotes
        .map((predioId, posicao) => {
            const predio = prediosPorId[predioId];
            const tema = predio ? temasConstrucoes[predio.tipo] : "vazio";
            const titulo = predio ? `${predio.nome} · Nivel ${predio.nivel}` : "Terreno livre";
            const selecionavel = !predio && (construcaoSelecionada || predioEmMovimento);
            const invalido = predio && (construcaoSelecionada || predioEmMovimento);
            return `
                <button type="button" class="lote lote-${tema} ${predio ? "ocupado" : ""} ${selecionavel ? "selecionavel" : ""} ${invalido ? "invalido" : ""}"
                    data-posicao="${posicao}" ${predio ? `data-predio="${predio.id}"` : ""} title="${titulo}">
                    <span class="predio" aria-hidden="true"></span>
                    <strong>${titulo}</strong>
                </button>
            `;
        })
        .join("");
}

function desenharConstrucoes(estado) {
    const construcoes = estado.construcoes_disponiveis;
    if (!categoriaSelecionada || !estado.categorias_construcoes.some((item) => item.id === categoriaSelecionada)) {
        categoriaSelecionada = estado.categorias_construcoes[0]?.id;
    }
    elementos.categoriasConstrucoes.innerHTML = estado.categorias_construcoes.map((categoria) => `
        <button type="button" data-categoria="${categoria.id}" class="${categoria.id === categoriaSelecionada ? "ativa" : ""}">${categoria.nome}</button>
    `).join("");
    elementos.listaConstrucoes.innerHTML = construcoes
        .filter((construcao) => construcao.categoria === categoriaSelecionada)
        .map((construcao) => {
            const falta = Math.max(0, construcao.custo - estado.cidade.dados.dinheiro);
            const custos = [
                construcao.consumo_energia ? `-${construcao.consumo_energia} energia` : "",
                construcao.consumo_agua ? `-${construcao.consumo_agua} agua` : "",
                `-${formatarDinheiro(construcao.manutencao)}/rodada`,
            ].filter(Boolean).join(" · ");
            return `
                <article class="card-construcao card-${temasConstrucoes[construcao.id] || "vazio"}">
                    <div><strong>${construcao.nome}</strong><b>${formatarDinheiro(construcao.custo)}</b></div>
                    <p class="beneficio">${construcao.beneficio_principal}</p>
                    <small>${custos}</small>
                    <button type="button" data-construcao="${construcao.id}" ${falta ? "disabled" : ""}>
                        ${falta ? `Faltam ${formatarDinheiro(falta)}` : "Selecionar"}
                    </button>
                </article>
            `;
        })
        .join("");
}

function desenharEvento(evento) {
    elementos.eventoAtivo.innerHTML = evento
        ? `<strong>${evento.titulo}</strong><p>${evento.descricao}</p>`
        : "<strong>Cidade estavel</strong><p>Nenhum evento ativo nesta rodada.</p>";
}

function desenharHistorico(itens) {
    elementos.historico.innerHTML = itens.map((item) => `<li>${item}</li>`).join("");
}

function desenharAlertas(dados, economia) {
    const alertas = [];
    const adicionar = (prioridade, titulo, texto) => alertas.push({ prioridade, titulo, texto });
    const avaliarBaixo = (valor, nome) => {
        if (valor <= 25) adicionar(3, `${nome} em nivel critico`, `${valor}% disponivel. Priorize infraestrutura.`);
        else if (valor <= 40) adicionar(2, `${nome} exige atencao`, `${valor}% disponivel.`);
    };

    const avaliarRecurso = (valor, nome) => {
        if (valor > 100) adicionar(3, `${nome} em sobrecarga`, `${valor}% de utilizacao. Predios operam com eficiencia reduzida.`);
        else if (valor >= 85) adicionar(2, `${nome} proxima do limite`, `${valor}% da capacidade utilizada.`);
    };
    avaliarRecurso(dados.energia, "Energia");
    avaliarRecurso(dados.agua, "Agua");
    avaliarBaixo(dados.saude, "Saude");
    avaliarBaixo(dados.educacao, "Educacao");

    if (dados.qualidade_vida < 35) adicionar(3, "Qualidade de vida critica", `${dados.qualidade_vida}% de bem-estar.`);
    else if (dados.qualidade_vida < 50) adicionar(2, "Qualidade de vida em queda", `${dados.qualidade_vida}% de bem-estar.`);
    if (dados.poluicao >= 70) adicionar(3, "Poluicao critica", `${dados.poluicao}% de poluicao.`);
    else if (dados.poluicao >= 50) adicionar(2, "Poluicao elevada", `${dados.poluicao}% de poluicao.`);

    const taxaDesemprego = economia.taxa_desemprego;
    if (taxaDesemprego >= 50) adicionar(3, "Desemprego muito alto", `${taxaDesemprego}% da populacao ativa sem trabalho.`);
    else if (taxaDesemprego >= 30) adicionar(2, "Desemprego alto", `${taxaDesemprego}% da populacao ativa sem trabalho.`);
    if (dados.dinheiro < 0) adicionar(3, "Caixa municipal negativo", formatarDinheiro(dados.dinheiro));

    if (!alertas.length) adicionar(1, "Cidade estavel", "Nenhum indicador exige resposta imediata.");
    elementos.listaAlertas.innerHTML = alertas
        .sort((a, b) => b.prioridade - a.prioridade)
        .slice(0, 3)
        .map(({ prioridade, titulo, texto }) => `
            <article class="alerta ${prioridade === 3 ? "alerta-critico" : prioridade === 2 ? "alerta-atencao" : ""}">
                <strong>${titulo}</strong><span>${texto}</span>
            </article>
        `)
        .join("");
}

function atualizarTimer({ rodada, rodadaMaxima, segundos, progresso, pausado, processando }) {
    elementos.numeroRodada.textContent = `Rodada ${String(rodada).padStart(2, "0")}/${rodadaMaxima}`;
    elementos.tempoRodada.textContent = formatarTempo(segundos);
    elementos.calendarioRodada.textContent = obterCalendario(rodada);
    elementos.progressoTempo.style.width = `${Math.max(0, Math.min(100, progresso * 100))}%`;
    elementos.timerCard.classList.toggle("atencao", !pausado && segundos <= 15 && segundos > 5);
    elementos.timerCard.classList.toggle("critico", !pausado && segundos <= 5);
    elementos.timerCard.classList.toggle("pausado", pausado);
    elementos.botaoPausa.disabled = processando;
    elementos.botaoPausa.textContent = pausado ? ">" : "II";
    elementos.botaoPausa.setAttribute("aria-label", pausado ? "Retomar jogo" : "Pausar jogo");
    elementos.segundosConfirmacao.textContent = `${segundos} ${segundos === 1 ? "segundo" : "segundos"}`;
}

function atualizarBloqueioAcoes() {
    if (!estadoAtual || !controladorRodadas) return;
    const bloqueado = controladorRodadas.rodadaProcessando
        || controladorRodadas.jogoPausado
        || estadoAtual.cidade.status !== "jogando";
    elementos.botaoFinalizar.disabled = bloqueado;
    elementos.listaConstrucoes.querySelectorAll("button").forEach((botao) => {
        const construcao = estadoAtual.construcoes_disponiveis.find(
            (item) => item.id === botao.dataset.construcao
        );
        botao.disabled = bloqueado || estadoAtual.cidade.dados.dinheiro < construcao.custo;
    });
    elementos.controlesImpostos.querySelectorAll("button").forEach((botao) => { botao.disabled = bloqueado; });
    elementos.painelPredio.querySelectorAll("button:not(.fechar-detalhe)").forEach((botao) => {
        if (botao.matches("[data-melhorar-predio]")) {
            const predio = estadoAtual.cidade.construcoes.find((item) => item.id === predioSelecionado);
            botao.disabled = bloqueado || !predio?.proximo_upgrade || estadoAtual.cidade.dados.dinheiro < predio.custo_upgrade;
        } else {
            botao.disabled = bloqueado;
        }
    });
}

function abrirPainel(nome) {
    if (!(nome in paineis)) return;
    Object.entries(paineis).forEach(([chave, painel]) => {
        painel.hidden = chave !== nome;
    });
    document.querySelectorAll("[data-painel]").forEach((botao) => {
        botao.classList.toggle("ativa", botao.dataset.painel === nome);
    });
    elementos.tituloPainel.textContent = titulosPaineis[nome];
    elementos.painelOperacional.classList.add("aberto");
    elementos.painelOperacional.setAttribute("aria-hidden", "false");
    painelAberto = nome;
}

function fecharPainel() {
    elementos.painelOperacional.classList.remove("aberto");
    elementos.painelOperacional.setAttribute("aria-hidden", "true");
    document.querySelectorAll("[data-painel]").forEach((botao) => botao.classList.remove("ativa"));
    painelAberto = null;
}

function definirModal(modal, aberto) {
    modal.setAttribute("aria-hidden", aberto ? "false" : "true");
}

function alternarPausa() {
    if (!controladorRodadas || controladorRodadas.rodadaProcessando) return;
    if (controladorRodadas.jogoPausado) {
        definirModal(elementos.modalPausa, false);
        controladorRodadas.retomar();
    } else if (controladorRodadas.pausar()) {
        definirModal(elementos.modalPausa, true);
    }
    atualizarBloqueioAcoes();
}

function cancelarAcaoMapa() {
    construcaoSelecionada = null;
    predioEmMovimento = null;
    elementos.selecaoConstrucao.hidden = true;
    if (estadoAtual) desenharMapa(estadoAtual.cidade.mapa);
}

function selecionarConstrucao(tipo) {
    construcaoSelecionada = tipo;
    predioEmMovimento = null;
    const dados = estadoAtual.construcoes_disponiveis.find((item) => item.id === tipo);
    elementos.selecaoConstrucao.hidden = false;
    elementos.selecaoConstrucao.innerHTML = `<strong>${dados.nome} selecionada.</strong> Escolha um terreno verde. <button type="button" data-cancelar-acao>Cancelar</button>`;
    fecharPainel();
    desenharMapa(estadoAtual.cidade.mapa);
}

async function construir(construcaoId, posicao) {
    if (!controladorRodadas?.rodadaAtiva || controladorRodadas.jogoPausado) return;
    try {
        const resposta = await chamarApi("/api/construir", {
            construcao_id: construcaoId,
            posicao,
        });
        atualizarTela(resposta, resposta.mensagem);
        if (resposta.sucesso) cancelarAcaoMapa();
    } catch (erro) {
        elementos.mensagem.textContent = erro.message;
    }
}

async function executarAcaoPredio(url, dados) {
    if (!controladorRodadas?.rodadaAtiva || controladorRodadas.jogoPausado) {
        return { sucesso: false };
    }
    const resposta = await chamarApi(url, dados);
    atualizarTela(resposta, resposta.mensagem);
    return resposta;
}

function abrirDetalhesPredio(predioId) {
    const predio = estadoAtual.cidade.construcoes.find((item) => item.id === predioId);
    if (!predio) {
        fecharDetalhesPredio();
        return;
    }
    predioSelecionado = predioId;
    const upgrade = predio.proximo_upgrade;
    const beneficios = [
        ["Moradia", predio.capacidade_populacional], ["Saude", predio.capacidade_saude],
        ["Educacao", predio.capacidade_educacao], ["Gera agua", predio.gera_agua],
        ["Gera energia", predio.gera_energia], ["Poluicao", predio.poluicao],
    ].filter(([, valor]) => valor).map(([nome, valor]) => `<dt>${nome}</dt><dd>${valor > 0 ? "+" : ""}${valor}</dd>`).join("");
    elementos.painelPredio.setAttribute("aria-hidden", "false");
    elementos.painelPredio.innerHTML = `
        <button class="fechar-detalhe" type="button" data-fechar-predio>×</button>
        <span class="rotulo">${predio.categoria}</span><h2>${predio.nome}</h2><strong>Nivel ${predio.nivel}</strong>
        <dl class="lista-economia">
            ${beneficios}
            <dt>Empregos</dt><dd>+${predio.empregos}</dd><dt>Manutencao</dt><dd>${formatarDinheiro(predio.manutencao)}</dd>
            <dt>Energia</dt><dd>-${predio.consumo_energia}</dd><dt>Agua</dt><dd>-${predio.consumo_agua}</dd>
            <dt>Eficiencia</dt><dd>${predio.eficiencia}%</dd>
        </dl>
        ${predio.motivos_ineficiencia.map((motivo) => `<p class="aviso-eficiencia">${motivo}</p>`).join("")}
        <div class="acoes-predio">
            <button type="button" data-melhorar-predio ${!upgrade || estadoAtual.cidade.dados.dinheiro < predio.custo_upgrade ? "disabled" : ""}>${upgrade ? `Melhorar · ${formatarDinheiro(predio.custo_upgrade)}` : "Nivel maximo"}</button>
            <button type="button" data-mover-predio>Mover</button><button type="button" class="perigo" data-demolir-predio>Demolir</button>
        </div>`;
}

function fecharDetalhesPredio() {
    predioSelecionado = null;
    elementos.painelPredio.setAttribute("aria-hidden", "true");
    elementos.painelPredio.innerHTML = "";
}

function iniciarMovimento(predioId) {
    predioEmMovimento = predioId;
    construcaoSelecionada = null;
    fecharDetalhesPredio();
    elementos.selecaoConstrucao.hidden = false;
    elementos.selecaoConstrucao.innerHTML = `<strong>Movendo predio.</strong> Escolha um terreno verde. <button type="button" data-cancelar-acao>Cancelar</button>`;
    fecharPainel();
    desenharMapa(estadoAtual.cidade.mapa);
}

function criarItensResumo(resumo) {
    const variacoes = resumo.variacoes || {};
    const itens = [
        ["dinheiro", "Caixa", (valor) => `${valor >= 0 ? "+" : "-"}${formatarDinheiro(Math.abs(valor))}`],
        ["populacao", "habitantes", (valor) => `${valor >= 0 ? "+" : ""}${valor} habitantes`],
        ["empregos", "empregos", (valor) => `${valor >= 0 ? "+" : ""}${valor} empregos`],
        ["qualidade_vida", "qualidade de vida", (valor) => `${valor >= 0 ? "+" : ""}${valor} qualidade de vida`],
    ];
    const linhas = itens
        .filter(([chave]) => variacoes[chave] !== 0)
        .map(([chave, , formatar]) => `<li>${formatar(variacoes[chave])}</li>`);
    return linhas.length ? linhas.join("") : "<li>Indicadores permaneceram estaveis.</li>";
}

async function mostrarResumo(resposta) {
    const duracao = resposta.config_rodadas.duracao_resumo;
    elementos.faseTransicao.textContent = "Cidade processada";
    elementos.tituloResumo.textContent = `Rodada ${resposta.resumo.rodada} concluida`;
    elementos.itensResumo.innerHTML = criarItensResumo(resposta.resumo);

    for (let restante = duracao; restante > 0; restante -= 1) {
        elementos.contagemProxima.textContent = resposta.cidade.status === "jogando"
            ? `Proxima rodada em ${restante}...`
            : "Partida concluida";
        await esperar(1000);
    }
}

async function processarFimDaRodada({ rodada }) {
    definirModal(elementos.modalConfirmacao, false);
    definirModal(elementos.modalDemolicao, false);
    cancelarAcaoMapa();
    fecharDetalhesPredio();
    fecharPainel();
    elementos.overlayTransicao.setAttribute("aria-hidden", "false");
    elementos.faseTransicao.textContent = "Processando cidade...";
    elementos.tituloResumo.textContent = `Encerrando rodada ${rodada}`;
    elementos.itensResumo.innerHTML = "";
    elementos.contagemProxima.textContent = "";
    atualizarBloqueioAcoes();

    try {
        const resposta = await chamarApi("/api/proxima-rodada", { rodada_esperada: rodada });
        await esperar(350);
        atualizarTela(resposta, resposta.mensagem);

        if (resposta.rodada_ja_processada) {
            elementos.overlayTransicao.setAttribute("aria-hidden", "true");
            controladorRodadas.iniciar(resposta.cidade.dados.rodada, resposta.cidade.dados.max_rodadas);
            atualizarBloqueioAcoes();
            return;
        }

        await mostrarResumo(resposta);
        if (resposta.cidade.status === "jogando") {
            elementos.overlayTransicao.setAttribute("aria-hidden", "true");
            controladorRodadas.iniciar(resposta.cidade.dados.rodada, resposta.cidade.dados.max_rodadas);
            atualizarBloqueioAcoes();
        } else {
            controladorRodadas.parar();
            elementos.contagemProxima.innerHTML = '<a class="botao-secundario" href="/">Voltar ao menu</a>';
        }
    } catch (erro) {
        elementos.faseTransicao.textContent = "Falha ao processar";
        elementos.tituloResumo.textContent = erro.message;
        elementos.contagemProxima.innerHTML = '<a class="botao-secundario" href="/">Voltar ao menu</a>';
    }
}

async function iniciarJogo() {
    const parametros = new URLSearchParams(window.location.search);
    const prefeito = (parametros.get("prefeito") || "").trim();

    try {
        const estado = await chamarApi("/api/novo-jogo", { prefeito });
        controladorRodadas = new ControladorRodadas({
            config: estado.config_rodadas,
            aoAtualizar: atualizarTimer,
            aoEncerrar: processarFimDaRodada,
        });
        atualizarTela(estado, "Analise as prioridades e administre antes que o tempo termine.");
        controladorRodadas.iniciar(estado.cidade.dados.rodada, estado.cidade.dados.max_rodadas);
    } catch (erro) {
        elementos.mensagem.textContent = erro.message;
    }
}

document.querySelectorAll("[data-painel]").forEach((botao) => {
    botao.addEventListener("click", () => {
        const nome = botao.dataset.painel;
        if (painelAberto === nome) fecharPainel();
        else abrirPainel(nome);
    });
});

elementos.fecharPainel.addEventListener("click", fecharPainel);
elementos.listaConstrucoes.addEventListener("click", (evento) => {
    const botao = evento.target.closest("[data-construcao]");
    if (botao && !botao.disabled) selecionarConstrucao(botao.dataset.construcao);
});
elementos.categoriasConstrucoes.addEventListener("click", (evento) => {
    const botao = evento.target.closest("[data-categoria]");
    if (botao) {
        categoriaSelecionada = botao.dataset.categoria;
        desenharConstrucoes(estadoAtual);
        atualizarBloqueioAcoes();
    }
});
elementos.selecaoConstrucao.addEventListener("click", (evento) => {
    if (evento.target.closest("[data-cancelar-acao]")) cancelarAcaoMapa();
});
elementos.mapa.addEventListener("click", async (evento) => {
    const lote = evento.target.closest("[data-posicao]");
    if (!lote) return;
    if (construcaoSelecionada) {
        if (lote.dataset.predio) elementos.mensagem.textContent = "Area ocupada.";
        else await construir(construcaoSelecionada, Number(lote.dataset.posicao));
    } else if (predioEmMovimento) {
        if (lote.dataset.predio) elementos.mensagem.textContent = "Area ocupada.";
        else {
            const resposta = await executarAcaoPredio("/api/mover", { predio_id: predioEmMovimento, posicao: Number(lote.dataset.posicao) });
            if (resposta.sucesso) cancelarAcaoMapa();
        }
    } else if (lote.dataset.predio) abrirDetalhesPredio(lote.dataset.predio);
});
elementos.controlesImpostos.addEventListener("click", async (evento) => {
    const botao = evento.target.closest("[data-imposto]");
    if (botao && !botao.disabled) await executarAcaoPredio("/api/imposto", { tipo: botao.dataset.imposto, direcao: Number(botao.dataset.direcao) });
});
elementos.painelPredio.addEventListener("click", async (evento) => {
    if (evento.target.closest("[data-fechar-predio]")) fecharDetalhesPredio();
    else if (evento.target.closest("[data-mover-predio]")) iniciarMovimento(predioSelecionado);
    else if (evento.target.closest("[data-melhorar-predio]")) await executarAcaoPredio("/api/melhorar", { predio_id: predioSelecionado });
    else if (evento.target.closest("[data-demolir-predio]")) {
        const predio = estadoAtual.cidade.construcoes.find((item) => item.id === predioSelecionado);
        elementos.tituloDemolicao.textContent = `Demolir ${predio.nome}?`;
        elementos.reembolsoDemolicao.textContent = formatarDinheiro(Math.round(predio.investimento * estadoAtual.config_construcoes.reembolso_demolicao));
        definirModal(elementos.modalDemolicao, true);
    }
});
elementos.cancelarDemolicao.addEventListener("click", () => definirModal(elementos.modalDemolicao, false));
elementos.confirmarDemolicao.addEventListener("click", async () => {
    const resposta = await executarAcaoPredio("/api/demolir", { predio_id: predioSelecionado });
    definirModal(elementos.modalDemolicao, false);
    if (resposta.sucesso) fecharDetalhesPredio();
});
elementos.botaoPausa.addEventListener("click", alternarPausa);
elementos.botaoRetomar.addEventListener("click", alternarPausa);
elementos.botaoFinalizar.addEventListener("click", () => definirModal(elementos.modalConfirmacao, true));
elementos.cancelarFinalizacao.addEventListener("click", () => definirModal(elementos.modalConfirmacao, false));
elementos.confirmarFinalizacao.addEventListener("click", () => controladorRodadas?.encerrar("manual"));

document.addEventListener("visibilitychange", () => controladorRodadas?.sincronizar());
document.addEventListener("keydown", (evento) => {
    if (evento.target.matches("input, textarea")) return;
    const tecla = evento.key.toLowerCase();

    if (evento.key === "Escape") {
        if (elementos.modalDemolicao.getAttribute("aria-hidden") === "false") {
            definirModal(elementos.modalDemolicao, false);
        } else if (elementos.modalConfirmacao.getAttribute("aria-hidden") === "false") {
            definirModal(elementos.modalConfirmacao, false);
        } else if (construcaoSelecionada || predioEmMovimento) {
            cancelarAcaoMapa();
        } else if (predioSelecionado) {
            fecharDetalhesPredio();
        } else if (painelAberto) {
            fecharPainel();
        } else {
            alternarPausa();
        }
    } else if (tecla === "b") {
        abrirPainel("construir");
    } else if (tecla === "e") {
        abrirPainel("economia");
    }
});

window.addEventListener("beforeunload", () => controladorRodadas?.parar());

iniciarJogo();
