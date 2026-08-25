from copy import deepcopy

from .dados import DADOS_INICIAIS


INDICADORES_LIMITADOS = [
    "educacao",
    "saude",
    "energia",
    "agua",
    "poluicao",
    "qualidade_vida",
]


class Cidade:
    def __init__(self, prefeito="Prefeito"):
        self.prefeito = prefeito or "Prefeito"
        self.dados = deepcopy(DADOS_INICIAIS)
        self.construcoes = []
        self.mapa = [None for _ in range(16)]
        self.historico = []
        self.evento_ativo = None
        self.status = "jogando"
        self.rodadas_em_crise = 0

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
        self.dados["capacidade_populacional"] = max(
            self.dados["populacao"],
            self.dados["capacidade_populacional"],
        )

    def contar_construcoes(self):
        totais = {}
        for construcao_id in self.construcoes:
            totais[construcao_id] = totais.get(construcao_id, 0) + 1
        return totais

    def to_dict(self):
        return {
            "prefeito": self.prefeito,
            "dados": self.dados,
            "construcoes": self.contar_construcoes(),
            "mapa": self.mapa,
            "historico": self.historico[-6:],
            "evento_ativo": self.evento_ativo,
            "status": self.status,
            "rodadas_em_crise": self.rodadas_em_crise,
        }

