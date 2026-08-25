from .cidade import Cidade
from .construcoes import construir, listar_construcoes
from .economia import calcular_economia, processar_rodada
from .eventos import sortear_evento


class JogoCidade:
    def __init__(self):
        self.cidade = Cidade()

    def novo_jogo(self, prefeito):
        self.cidade = Cidade(prefeito)
        self.cidade.historico.append("Bem-vindo a Cidade em Equilibrio.")
        return self.estado()

    def estado(self):
        return {
            "cidade": self.cidade.to_dict(),
            "construcoes_disponiveis": listar_construcoes(),
            "economia": calcular_economia(self.cidade),
        }

    def construir(self, construcao_id, posicao=None):
        sucesso, mensagem = construir(self.cidade, construcao_id, posicao)
        self.cidade.historico.append(mensagem)
        return {"sucesso": sucesso, "mensagem": mensagem, **self.estado()}

    def proxima_rodada(self):
        if self.cidade.status != "jogando":
            return {
                "sucesso": False,
                "mensagem": "A partida ja terminou.",
                **self.estado(),
            }

        resumo = processar_rodada(self.cidade)
        evento = sortear_evento(self.cidade)

        mensagem = (
            f"Rodada {resumo['rodada']} processada. "
            f"Resultado: R$ {resumo['resultado']}."
        )
        if evento:
            mensagem += f" Evento: {evento['titulo']}."

        self.cidade.historico.append(mensagem)

        return {
            "sucesso": True,
            "mensagem": mensagem,
            "resumo": resumo,
            **self.estado(),
        }

