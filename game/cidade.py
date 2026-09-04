from copy import deepcopy

from .dados import (
    CONFIG_IMPOSTOS,
    CONFIG_MAPA,
    CONFIG_PRODUCAO,
    CONFIG_SIMULACAO,
    DADOS_INICIAIS,
    dados_construcao_nivel,
)
from .projetos import efeitos_projetos
from .territorio import calcular_transito, possui_acesso_viario


INDICADORES_LIMITADOS = ["educacao", "saude", "poluicao", "qualidade_vida"]


class Cidade:
    def __init__(self, prefeito="Prefeito"):
        self.prefeito = prefeito or "Prefeito"
        self.dados = deepcopy(DADOS_INICIAIS)
        self.impostos = deepcopy(CONFIG_IMPOSTOS["taxas_iniciais"])
        self.construcoes = []
        self.mapa = [None for _ in range(CONFIG_MAPA["total_celulas"])]
        self.setores_desbloqueados = {CONFIG_MAPA["setor_inicial"]}
        self.obstaculos = deepcopy(CONFIG_MAPA["obstaculos"])
        self.estradas = set()
        self.proximo_predio_id = 1
        self.historico = []
        self.historico_metricas = []
        self.evento_ativo = None
        self.eventos_ocorridos = {}
        self.modificadores = []
        self.proximo_modificador_id = 1
        self.consequencias_futuras = []
        self.proxima_consequencia_id = 1
        self.missoes_concluidas = set()
        self.pontos_progresso = 0
        self.ultimo_resultado = None
        self.status = "jogando"
        self.motivo_fim = None
        self.rodadas_em_crise = 0
        self.contadores_crise = {"financeira": 0, "social": 0, "infraestrutura": 0}
        self.crises_ativas = []
        self.crises_resolvidas = 0
        self.avaliacao_final = None
        self.estoque = deepcopy(CONFIG_PRODUCAO["estoque_inicial"])
        self.fatores_producao = {"comercio": 1, "alimentos": 1}
        self.pedido_ativo = None
        self.pedidos_finalizados = set()
        self.projetos_em_andamento = {}
        self.projetos_concluidos = set()
        # O cronometro faz parte do estado da partida. Assim ele sobrevive a
        # recarregamentos da pagina e nao pode ser reiniciado pelo navegador.
        self.timer = {
            "rodada": self.dados["rodada"],
            "restante_ms": 0,
            "fim_em_ms": None,
            "pausado": True,
            "motivo_pausa": "inicio",
        }
        self.simulacao = {}
        self.simulacao_suja = True

    def marcar_simulacao_suja(self):
        self.simulacao_suja = True

    def valor_modificador(self, alvo):
        return sum(item["valor"] for item in self.modificadores if item["alvo"] == alvo)

    def registrar_historico(self, tipo, titulo, descricao, rodada=None):
        self.historico.append({
            "rodada": rodada if rodada is not None else self.dados["rodada"],
            "tipo": tipo,
            "titulo": titulo,
            "descricao": descricao,
        })

    def registrar_metricas(self, rodada, resultado):
        self.historico_metricas.append({
            "rodada": rodada,
            "dinheiro": self.dados["dinheiro"],
            "resultado": resultado,
            "populacao": self.dados["populacao"],
            "saude": self.dados["saude"],
            "educacao": self.dados["educacao"],
            "poluicao": self.dados["poluicao"],
            "qualidade_vida": self.dados["qualidade_vida"],
            "taxa_desemprego": self.simulacao["trabalho"]["taxa_desemprego"],
            "agua": self.dados["agua"],
            "energia": self.dados["energia"],
        })

    def limitar_indicadores(self):
        for chave in INDICADORES_LIMITADOS:
            self.dados[chave] = max(0, min(100, self.dados[chave]))
        self.dados["populacao"] = max(0, self.dados["populacao"])
        self.dados["empregos"] = max(0, self.dados["empregos"])

    def recalcular_simulacao(self):
        config = CONFIG_SIMULACAO
        populacao = self.dados["populacao"]
        predios_base = [
            (predio, dados_construcao_nivel(predio["tipo"], predio["nivel"]))
            for predio in self.construcoes
        ]
        projetos = efeitos_projetos(self)
        transito = calcular_transito(self)

        capacidade_energia = config["capacidade_base_energia"] + sum(d["gera_energia"] for _, d in predios_base) + projetos.get("gera_energia", 0)
        capacidade_agua = config["capacidade_base_agua"] + sum(d["gera_agua"] for _, d in predios_base) + projetos.get("gera_agua", 0)
        capacidade_energia *= max(0, 1 + self.valor_modificador("capacidade_energia_pct") / 100)
        capacidade_agua *= max(0, 1 + self.valor_modificador("capacidade_agua_pct") / 100)
        demanda_energia = populacao * config["demanda_energia_por_habitante"] + sum(d["consumo_energia"] for _, d in predios_base) + projetos.get("consumo_energia", 0)
        demanda_agua = populacao * config["demanda_agua_por_habitante"] + sum(d["consumo_agua"] for _, d in predios_base) + projetos.get("consumo_agua", 0)
        demanda_energia *= max(0, 1 + self.valor_modificador("demanda_energia_pct") / 100)
        demanda_agua *= max(0, 1 + self.valor_modificador("demanda_agua_pct") / 100)
        fator_energia = min(1, capacidade_energia / demanda_energia) if demanda_energia else 1
        fator_agua = min(1, capacidade_agua / demanda_agua) if demanda_agua else 1

        detalhes_predios = []
        totais = {
            "capacidade_populacional": DADOS_INICIAIS["capacidade_populacional"],
            "empregos": config["empregos_base"],
            "capacidade_saude": config["capacidade_base_saude"],
            "capacidade_educacao": config["capacidade_base_educacao"],
            "poluicao": config["poluicao_base"],
            "qualidade_bonus": projetos.get("qualidade_bonus", 0),
        }
        totais["empregos"] += projetos.get("empregos", 0)
        totais["capacidade_saude"] += projetos.get("capacidade_saude", 0)
        totais["capacidade_educacao"] += projetos.get("capacidade_educacao", 0)
        totais["poluicao"] += projetos.get("poluicao", 0)
        poluicao_fontes = {"Base urbana": config["poluicao_base"]}

        for predio, dados in predios_base:
            motivos = []
            fatores = []
            if dados["consumo_energia"]:
                fatores.append(fator_energia)
                if fator_energia < 1:
                    motivos.append("Energia insuficiente")
            if dados["consumo_agua"]:
                fatores.append(fator_agua)
                if fator_agua < 1:
                    motivos.append("Agua insuficiente")
            eficiencia = min(fatores, default=1)
            acesso_viario = possui_acesso_viario(self, predio["posicao"])
            if not acesso_viario:
                eficiencia *= CONFIG_MAPA["penalidade_sem_acesso"]
                motivos.append("Sem acesso viario")
            bonus_categoria = self.valor_modificador(f"eficiencia_{dados['categoria']}_pct")
            if dados["categoria"] in ("comercio", "industria"):
                bonus_categoria += self.valor_modificador("eficiencia_economica_pct")
            eficiencia = max(0, eficiencia * (1 + bonus_categoria / 100))

            for chave in ("capacidade_populacional", "empregos", "capacidade_saude", "capacidade_educacao"):
                totais[chave] += round(dados[chave] * eficiencia)
            impacto_poluicao = round(dados["poluicao"] * eficiencia)
            totais["poluicao"] += impacto_poluicao
            totais["qualidade_bonus"] += dados.get("qualidade_bonus", 0) * eficiencia
            if impacto_poluicao:
                poluicao_fontes[dados["nome"]] = poluicao_fontes.get(dados["nome"], 0) + impacto_poluicao

            proximo_nivel = predio["nivel"] + 1
            detalhes_predios.append({
                **predio,
                **dados,
                "eficiencia": round(eficiencia * 100),
                "motivos_ineficiencia": motivos,
                "atividade_efetiva": round(dados["atividade_economica"] * eficiencia),
                "acesso_viario": acesso_viario,
                "proximo_upgrade": (
                    dados_construcao_nivel(predio["tipo"], proximo_nivel)
                    if dados["custo_upgrade"] is not None else None
                ),
            })

        totais["empregos"] += self.valor_modificador("empregos_bonus")
        populacao_ativa = round(populacao * config["proporcao_populacao_ativa"])
        empregados = min(populacao_ativa, totais["empregos"])
        desempregados = max(0, populacao_ativa - empregados)
        taxa_desemprego = round(desempregados / populacao_ativa * 100) if populacao_ativa else 0
        cobertura_saude = min(100, round(totais["capacidade_saude"] / max(1, populacao * config["demanda_saude_por_habitante"]) * 100 + self.valor_modificador("saude_bonus")))
        cobertura_educacao = min(100, round(totais["capacidade_educacao"] / max(1, populacao * config["demanda_educacao_por_habitante"]) * 100 + self.valor_modificador("educacao_bonus")))
        utilizacao_energia = round(demanda_energia / capacidade_energia * 100) if capacidade_energia else 999
        utilizacao_agua = round(demanda_agua / capacidade_agua * 100) if capacidade_agua else 999
        poluicao_transito = round(max(0, transito["utilizacao"] - 100) * 0.05)
        poluicao = max(0, min(100, totais["poluicao"] + poluicao_transito + self.valor_modificador("poluicao_bonus")))
        if poluicao_transito:
            poluicao_fontes["Transito congestionado"] = poluicao_transito

        notas = {
            "saude": cobertura_saude,
            "educacao": cobertura_educacao,
            "emprego": round(empregados / populacao_ativa * 100) if populacao_ativa else 100,
            "agua": max(0, 100 - utilizacao_agua),
            "energia": max(0, 100 - utilizacao_energia),
            "ambiente": 100 - poluicao,
        }
        qualidade = sum(notas[chave] * peso for chave, peso in config["pesos_qualidade_vida"].items())
        media_impostos = sum(self.impostos.values()) / len(self.impostos)
        qualidade -= (media_impostos - CONFIG_IMPOSTOS["taxa_neutra"]) * CONFIG_IMPOSTOS["impacto_qualidade_por_ponto"]
        qualidade += self.valor_modificador("qualidade_bonus")
        qualidade += totais["qualidade_bonus"]
        qualidade -= max(0, transito["utilizacao"] - 100) * 0.05
        qualidade -= (1 - self.fatores_producao["alimentos"]) * CONFIG_PRODUCAO["penalidade_qualidade_falta_alimentos"]

        self.dados.update({
            "capacidade_populacional": totais["capacidade_populacional"],
            "empregos": totais["empregos"],
            "saude": cobertura_saude,
            "educacao": cobertura_educacao,
            "energia": utilizacao_energia,
            "agua": utilizacao_agua,
            "poluicao": poluicao,
            "qualidade_vida": round(qualidade),
        })
        self.limitar_indicadores()
        self.simulacao = {
            "predios": detalhes_predios,
            "energia": {"capacidade": round(capacidade_energia), "demanda": round(demanda_energia), "utilizacao": utilizacao_energia, "sobrecarga": max(0, round(demanda_energia - capacidade_energia))},
            "agua": {"capacidade": round(capacidade_agua), "demanda": round(demanda_agua), "utilizacao": utilizacao_agua, "sobrecarga": max(0, round(demanda_agua - capacidade_agua))},
            "saude": {"capacidade": totais["capacidade_saude"], "demanda": round(populacao * config["demanda_saude_por_habitante"]), "cobertura": cobertura_saude},
            "educacao": {"capacidade": totais["capacidade_educacao"], "demanda": round(populacao * config["demanda_educacao_por_habitante"]), "cobertura": cobertura_educacao},
            "trabalho": {"populacao_ativa": populacao_ativa, "empregados": empregados, "desempregados": desempregados, "taxa_desemprego": taxa_desemprego},
            "poluicao_fontes": poluicao_fontes,
            "notas_qualidade": notas,
            "transito": transito,
            "projetos_ativos": sorted(self.projetos_concluidos),
        }
        self.simulacao_suja = False

    def processar_populacao(self):
        config = CONFIG_SIMULACAO
        populacao_anterior = self.dados["populacao"]
        qualidade = self.dados["qualidade_vida"]
        crescimento = config["crescimento_populacional_base"]
        if qualidade >= 70:
            crescimento += 3
        elif qualidade < 35:
            crescimento -= 2
        if qualidade < 25:
            crescimento -= 3
        if self.simulacao["trabalho"]["taxa_desemprego"] > 35:
            crescimento -= 2
        if self.simulacao["energia"]["sobrecarga"] or self.simulacao["agua"]["sobrecarga"]:
            crescimento -= 2
        media_impostos = sum(self.impostos.values()) / len(self.impostos)
        crescimento -= round((media_impostos - CONFIG_IMPOSTOS["taxa_neutra"]) * CONFIG_IMPOSTOS["impacto_crescimento_por_ponto"])
        crescimento += round(self.valor_modificador("crescimento_populacao"))
        if self.fatores_producao["alimentos"] < 0.8:
            crescimento -= 2
        crescimento = max(-5, crescimento)
        nova_populacao = self.dados["populacao"] + crescimento
        self.dados["populacao"] = max(0, min(nova_populacao, self.dados["capacidade_populacional"]))
        self.marcar_simulacao_suja()
        return self.dados["populacao"] - populacao_anterior

    def exportar_persistencia(self):
        """Retorna somente dados serializaveis e necessarios para retomar a partida."""
        estado = deepcopy(self.__dict__)
        for chave in (
            "setores_desbloqueados",
            "estradas",
            "missoes_concluidas",
            "pedidos_finalizados",
            "projetos_concluidos",
        ):
            estado[chave] = sorted(estado[chave])
        estado["obstaculos"] = {str(posicao): valor for posicao, valor in estado["obstaculos"].items()}
        # A simulacao e derivada das demais informacoes e pode mudar entre versoes.
        estado["simulacao"] = {}
        estado["simulacao_suja"] = True
        return estado

    @classmethod
    def restaurar_persistencia(cls, estado):
        cidade = cls(estado.get("prefeito", "Prefeito"))
        for chave, valor in estado.items():
            if hasattr(cidade, chave):
                setattr(cidade, chave, deepcopy(valor))
        for chave in (
            "setores_desbloqueados",
            "estradas",
            "missoes_concluidas",
            "pedidos_finalizados",
            "projetos_concluidos",
        ):
            setattr(cidade, chave, set(getattr(cidade, chave)))
        cidade.obstaculos = {int(posicao): valor for posicao, valor in cidade.obstaculos.items()}
        cidade.simulacao = {}
        cidade.simulacao_suja = True
        return cidade

    def to_dict(self):
        if self.simulacao_suja:
            self.recalcular_simulacao()
        return {
            "prefeito": self.prefeito,
            "dados": deepcopy(self.dados),
            "impostos": deepcopy(self.impostos),
            "construcoes": deepcopy(self.simulacao["predios"]),
            "mapa": self.mapa.copy(),
            "simulacao": deepcopy(self.simulacao),
            "historico": deepcopy(self.historico[-30:]),
            "historico_metricas": deepcopy(self.historico_metricas),
            "evento_ativo": deepcopy(self.evento_ativo),
            "modificadores": deepcopy(self.modificadores),
            "consequencias_futuras": deepcopy(self.consequencias_futuras),
            "status": self.status,
            "motivo_fim": self.motivo_fim,
            "rodadas_em_crise": self.rodadas_em_crise,
            "avaliacao_final": deepcopy(self.avaliacao_final),
            "setores_desbloqueados": sorted(self.setores_desbloqueados),
            "estradas": sorted(self.estradas),
            "obstaculos": deepcopy(self.obstaculos),
            "estoque": deepcopy(self.estoque),
            "fatores_producao": deepcopy(self.fatores_producao),
            "pedido_ativo": deepcopy(self.pedido_ativo),
            "pedidos_finalizados": sorted(self.pedidos_finalizados),
            "projetos_em_andamento": deepcopy(self.projetos_em_andamento),
            "projetos_concluidos": sorted(self.projetos_concluidos),
        }
