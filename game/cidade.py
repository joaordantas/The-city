from copy import deepcopy

from .dados import (
    CONFIG_IMPOSTOS,
    CONFIG_SIMULACAO,
    DADOS_INICIAIS,
    dados_construcao_nivel,
)


INDICADORES_LIMITADOS = ["educacao", "saude", "poluicao", "qualidade_vida"]


class Cidade:
    def __init__(self, prefeito="Prefeito"):
        self.prefeito = prefeito or "Prefeito"
        self.dados = deepcopy(DADOS_INICIAIS)
        self.impostos = deepcopy(CONFIG_IMPOSTOS["taxas_iniciais"])
        self.construcoes = []
        self.mapa = [None for _ in range(16)]
        self.proximo_predio_id = 1
        self.historico = []
        self.evento_ativo = None
        self.status = "jogando"
        self.rodadas_em_crise = 0
        self.simulacao = {}
        self.simulacao_suja = True

    def marcar_simulacao_suja(self):
        self.simulacao_suja = True

    def aplicar_efeitos(self, efeitos):
        for chave, valor in efeitos.items():
            if chave in self.dados:
                self.dados[chave] += valor
        self.limitar_indicadores()

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

        capacidade_energia = config["capacidade_base_energia"] + sum(d["gera_energia"] for _, d in predios_base)
        capacidade_agua = config["capacidade_base_agua"] + sum(d["gera_agua"] for _, d in predios_base)
        demanda_energia = populacao * config["demanda_energia_por_habitante"] + sum(d["consumo_energia"] for _, d in predios_base)
        demanda_agua = populacao * config["demanda_agua_por_habitante"] + sum(d["consumo_agua"] for _, d in predios_base)
        fator_energia = min(1, capacidade_energia / demanda_energia) if demanda_energia else 1
        fator_agua = min(1, capacidade_agua / demanda_agua) if demanda_agua else 1

        detalhes_predios = []
        totais = {
            "capacidade_populacional": DADOS_INICIAIS["capacidade_populacional"],
            "empregos": config["empregos_base"],
            "capacidade_saude": config["capacidade_base_saude"],
            "capacidade_educacao": config["capacidade_base_educacao"],
            "poluicao": config["poluicao_base"],
        }
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

            for chave in ("capacidade_populacional", "empregos", "capacidade_saude", "capacidade_educacao"):
                totais[chave] += round(dados[chave] * eficiencia)
            impacto_poluicao = round(dados["poluicao"] * eficiencia)
            totais["poluicao"] += impacto_poluicao
            if impacto_poluicao:
                poluicao_fontes[dados["nome"]] = poluicao_fontes.get(dados["nome"], 0) + impacto_poluicao

            proximo_nivel = predio["nivel"] + 1
            detalhes_predios.append({
                **predio,
                **dados,
                "eficiencia": round(eficiencia * 100),
                "motivos_ineficiencia": motivos,
                "atividade_efetiva": round(dados["atividade_economica"] * eficiencia),
                "proximo_upgrade": (
                    dados_construcao_nivel(predio["tipo"], proximo_nivel)
                    if dados["custo_upgrade"] is not None else None
                ),
            })

        populacao_ativa = round(populacao * config["proporcao_populacao_ativa"])
        empregados = min(populacao_ativa, totais["empregos"])
        desempregados = max(0, populacao_ativa - empregados)
        taxa_desemprego = round(desempregados / populacao_ativa * 100) if populacao_ativa else 0
        cobertura_saude = min(100, round(totais["capacidade_saude"] / max(1, populacao * config["demanda_saude_por_habitante"]) * 100))
        cobertura_educacao = min(100, round(totais["capacidade_educacao"] / max(1, populacao * config["demanda_educacao_por_habitante"]) * 100))
        utilizacao_energia = round(demanda_energia / capacidade_energia * 100) if capacidade_energia else 999
        utilizacao_agua = round(demanda_agua / capacidade_agua * 100) if capacidade_agua else 999
        poluicao = max(0, min(100, totais["poluicao"]))

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
            "energia": {"capacidade": capacidade_energia, "demanda": round(demanda_energia), "utilizacao": utilizacao_energia, "sobrecarga": max(0, round(demanda_energia - capacidade_energia))},
            "agua": {"capacidade": capacidade_agua, "demanda": round(demanda_agua), "utilizacao": utilizacao_agua, "sobrecarga": max(0, round(demanda_agua - capacidade_agua))},
            "saude": {"capacidade": totais["capacidade_saude"], "demanda": round(populacao * config["demanda_saude_por_habitante"]), "cobertura": cobertura_saude},
            "educacao": {"capacidade": totais["capacidade_educacao"], "demanda": round(populacao * config["demanda_educacao_por_habitante"]), "cobertura": cobertura_educacao},
            "trabalho": {"populacao_ativa": populacao_ativa, "empregados": empregados, "desempregados": desempregados, "taxa_desemprego": taxa_desemprego},
            "poluicao_fontes": poluicao_fontes,
            "notas_qualidade": notas,
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
        crescimento = max(-5, crescimento)
        nova_populacao = self.dados["populacao"] + crescimento
        self.dados["populacao"] = max(0, min(nova_populacao, self.dados["capacidade_populacional"]))
        self.marcar_simulacao_suja()
        return self.dados["populacao"] - populacao_anterior

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
            "historico": self.historico[-6:].copy(),
            "evento_ativo": deepcopy(self.evento_ativo),
            "status": self.status,
            "rodadas_em_crise": self.rodadas_em_crise,
        }
