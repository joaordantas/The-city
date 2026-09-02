function dinheiro(valor) {
    return `R$ ${Number(valor).toLocaleString("pt-BR")}`;
}

export function criarSistemasAvancados({ chamarApi, aoAtualizar, aoMensagem, aoSom }) {
    const elementos = {
        estoque: document.getElementById("estoque-recursos"),
        previsao: document.getElementById("previsao-producao"),
        pedido: document.getElementById("pedido-logistico"),
        projetos: document.getElementById("lista-projetos"),
        setores: document.getElementById("lista-setores"),
        transito: document.getElementById("estado-transito"),
        modalExpansao: document.getElementById("modal-expansao"),
    };
    let estado = null;
    let modoMapa = null;

    const agir = async (url, dados = null) => {
        try {
            const resposta = await chamarApi(url, dados);
            aoSom(resposta.sucesso ? "confirmar" : "erro");
            aoAtualizar(resposta, resposta.mensagem);
            return resposta;
        } catch (erro) {
            aoSom("erro");
            aoMensagem(erro.message);
            return null;
        }
    };

    function desenhar(novoEstado) {
        estado = novoEstado;
        const botaoEstrada = document.querySelector("[data-modo-mapa]");
        const botaoExpansao = document.querySelector("[data-abrir-expansao]");
        botaoEstrada.disabled = !estado.progressao.sistemas.estradas.desbloqueado;
        botaoEstrada.title = botaoEstrada.disabled ? "Disponivel na rodada 3" : "Selecione um terreno livre";
        botaoExpansao.disabled = !estado.progressao.sistemas.expansao.desbloqueado;
        botaoExpansao.title = botaoExpansao.disabled ? "Disponivel na rodada 6" : "Comprar um novo setor";
        const producao = estado.producao;
        const nomes = { alimentos: "Alimentos", materiais: "Materiais", mercadorias: "Mercadorias" };
        elementos.estoque.innerHTML = Object.entries(producao.estoque).map(([id, valor]) => {
            const percentual = Math.min(100, valor / producao.capacidade * 100);
            const alerta = percentual >= 90 ? " Estoque quase cheio." : valor === 0 ? " Sem reservas." : "";
            return `<article class="recurso-card"><div><strong>${nomes[id]}</strong><span>${valor}/${producao.capacidade}</span></div><meter min="0" max="${producao.capacidade}" value="${valor}"></meter><small>${alerta}</small></article>`;
        }).join("");
        elementos.previsao.innerHTML = Object.entries(producao.previsao.produzido).map(([id, valor]) => `<p><strong>${nomes[id]}</strong><span>+${valor}/rodada</span></p>`).join("") +
            `<small>Demanda: ${producao.previsao.demanda_alimentos} alimentos e ${producao.previsao.demanda_mercadorias} mercadorias.</small>`;

        const pedido = estado.logistica.pedido_ativo;
        elementos.pedido.innerHTML = pedido ? `<article class="pedido-card"><strong>${pedido.titulo}</strong><p>${Object.entries(pedido.recursos).map(([id, valor]) => `${valor} ${nomes[id].toLowerCase()}`).join(" · ")}</p><b>Recompensa: ${dinheiro(pedido.recompensa)}</b><div><button data-entregar-pedido type="button">Entregar</button><button data-recusar-pedido type="button">Guardar recursos</button></div></article>` : '<p class="sem-conteudo">Nenhum pedido ativo.</p>';

        elementos.projetos.innerHTML = estado.projetos.map((projeto) => {
            const custo = projeto.proxima_etapa;
            const status = projeto.concluido ? "Concluido" : projeto.disponivel ? `Etapa ${projeto.etapa_atual + 1}/${projeto.total_etapas}` : `Disponivel na rodada ${projeto.rodada_desbloqueio}`;
            return `<article class="projeto-card ${projeto.concluido ? "concluido" : ""}"><div><span>${status}</span><h3>${projeto.nome}</h3></div><p>${projeto.descricao}</p>${custo ? `<small>${dinheiro(custo.dinheiro)} + ${custo.materiais} materiais</small>` : ""}<button data-investir-projeto="${projeto.id}" type="button" ${!projeto.disponivel || projeto.concluido ? "disabled" : ""}>${projeto.concluido ? "Beneficios ativos" : "Investir na etapa"}</button></article>`;
        }).join("");

        const transito = estado.territorio.transito;
        elementos.transito.textContent = `Transito: ${transito.estado} · ${transito.utilizacao}%`;
        elementos.setores.innerHTML = estado.territorio.setores.filter((setor) => setor.id !== "centro").map((setor) => `<article><div><strong>${setor.nome}</strong><small>${setor.distrito}</small></div><span>${setor.desbloqueado ? "Desbloqueado" : dinheiro(setor.custo)}</span><button data-expandir-setor="${setor.id}" type="button" ${setor.desbloqueado ? "disabled" : ""}>${setor.desbloqueado ? "Concluido" : "Desbloquear"}</button></article>`).join("");
    }

    document.getElementById("acoes-territorio").addEventListener("click", (evento) => {
        if (evento.target.closest("[data-modo-mapa]")) {
            modoMapa = modoMapa === "estrada" ? null : "estrada";
            aoMensagem(modoMapa ? "Escolha um terreno para construir a estrada." : "Construcao de estrada cancelada.");
        }
        if (evento.target.closest("[data-abrir-expansao]")) elementos.modalExpansao.setAttribute("aria-hidden", "false");
    });
    document.getElementById("fechar-expansao").addEventListener("click", () => elementos.modalExpansao.setAttribute("aria-hidden", "true"));
    elementos.setores.addEventListener("click", async (evento) => {
        const botao = evento.target.closest("[data-expandir-setor]");
        if (botao) await agir("/api/expandir", { setor_id: botao.dataset.expandirSetor });
    });
    elementos.estoque.parentElement.parentElement.addEventListener("click", async (evento) => {
        if (evento.target.closest("[data-entregar-pedido]")) await agir("/api/logistica/entregar", {});
        if (evento.target.closest("[data-recusar-pedido]")) await agir("/api/logistica/recusar", {});
    });
    elementos.projetos.addEventListener("click", async (evento) => {
        const botao = evento.target.closest("[data-investir-projeto]");
        if (botao && !botao.disabled) await agir("/api/projetos/investir", { projeto_id: botao.dataset.investirProjeto });
    });

    return {
        desenhar,
        cancelarModo: () => { modoMapa = null; },
        tratarLote: async (lote) => {
            if (!estado || !modoMapa) return false;
            const posicao = Number(lote.dataset.posicao);
            await agir("/api/construir-estrada", { posicao });
            modoMapa = null;
            return true;
        },
        removerObstaculo: async (posicao) => agir("/api/remover-obstaculo", { posicao }),
    };
}
