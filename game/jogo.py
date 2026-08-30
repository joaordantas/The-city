from threading import Lock

from .cidade import Cidade
from .construcoes import (
    construir,
    demolir,
    listar_categorias,
    listar_construcoes,
    melhorar,
    mover,
)
from .dados import CONFIG_IMPOSTOS, CONFIG_RODADAS, CONFIG_SIMULACAO
from .economia import calcular_economia, processar_rodada
from .eventos import sortear_evento


class JogoCidade:
    def __init__(self):
        self.cidade = Cidade()
        self._bloqueio = Lock()

    def novo_jogo(self, prefeito):
        with self._bloqueio:
            self.cidade = Cidade(prefeito)
            self.cidade.historico.append("Bem-vindo a Cidade em Equilibrio.")
            return self.estado()

    def estado(self):
        cidade = self.cidade.to_dict()
        return {
            "cidade": cidade,
            "construcoes_disponiveis": listar_construcoes(),
            "categorias_construcoes": listar_categorias(),
            "economia": calcular_economia(self.cidade),
            "config_rodadas": CONFIG_RODADAS,
            "config_impostos": {
                "minimo": CONFIG_IMPOSTOS["minimo"],
                "maximo": CONFIG_IMPOSTOS["maximo"],
                "passo": CONFIG_IMPOSTOS["passo"],
            },
            "config_construcoes": {"reembolso_demolicao": CONFIG_SIMULACAO["reembolso_demolicao"]},
        }

    def construir(self, tipo, posicao):
        with self._bloqueio:
            sucesso, mensagem, predio_id = construir(self.cidade, tipo, posicao)
            self.cidade.historico.append(mensagem)
            return {"sucesso": sucesso, "mensagem": mensagem, "predio_id": predio_id, **self.estado()}

    def mover(self, predio_id, posicao):
        with self._bloqueio:
            sucesso, mensagem = mover(self.cidade, predio_id, posicao)
            if sucesso:
                self.cidade.historico.append(mensagem)
            return {"sucesso": sucesso, "mensagem": mensagem, **self.estado()}

    def demolir(self, predio_id):
        with self._bloqueio:
            sucesso, mensagem, reembolso = demolir(self.cidade, predio_id)
            if sucesso:
                self.cidade.historico.append(mensagem)
            return {"sucesso": sucesso, "mensagem": mensagem, "reembolso": reembolso, **self.estado()}

    def melhorar(self, predio_id):
        with self._bloqueio:
            sucesso, mensagem = melhorar(self.cidade, predio_id)
            if sucesso:
                self.cidade.historico.append(mensagem)
            return {"sucesso": sucesso, "mensagem": mensagem, **self.estado()}

    def alterar_imposto(self, tipo, direcao):
        with self._bloqueio:
            if tipo not in self.cidade.impostos or direcao not in (-1, 1):
                return {"sucesso": False, "mensagem": "Alteracao de imposto invalida.", **self.estado()}
            atual = self.cidade.impostos[tipo]
            novo = atual + direcao * CONFIG_IMPOSTOS["passo"]
            novo = max(CONFIG_IMPOSTOS["minimo"], min(CONFIG_IMPOSTOS["maximo"], novo))
            if novo == atual:
                return {"sucesso": False, "mensagem": "Este imposto ja esta no limite.", **self.estado()}
            self.cidade.impostos[tipo] = novo
            self.cidade.marcar_simulacao_suja()
            return {"sucesso": True, "mensagem": f"Imposto alterado para {novo}%.", **self.estado()}

    def proxima_rodada(self, rodada_esperada=None):
        with self._bloqueio:
            rodada_atual = self.cidade.dados["rodada"]
            if rodada_esperada is not None and rodada_esperada != rodada_atual:
                return {"sucesso": False, "rodada_ja_processada": True, "mensagem": "Esta rodada ja foi processada.", **self.estado()}
            if self.cidade.status != "jogando":
                return {"sucesso": False, "mensagem": "A partida ja terminou.", **self.estado()}

            antes = self.cidade.dados.copy()
            resumo = processar_rodada(self.cidade)
            evento = sortear_evento(self.cidade)
            depois = self.cidade.dados
            resumo["variacoes"] = {
                chave: depois[chave] - antes[chave]
                for chave in ("dinheiro", "populacao", "empregos", "qualidade_vida")
            }
            mensagem = f"Rodada {resumo['rodada']} processada. Resultado: R$ {resumo['resultado']}."
            if evento:
                mensagem += f" Evento: {evento['titulo']}."
            self.cidade.historico.append(mensagem)
            return {"sucesso": True, "mensagem": mensagem, "resumo": resumo, **self.estado()}
