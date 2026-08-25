import random

from .dados import EVENTOS


def sortear_evento(cidade):
    if cidade.dados["rodada"] <= 1:
        cidade.evento_ativo = None
        return None

    rolagem = random.randint(1, 100)
    acumulado = 0

    for evento in EVENTOS:
        acumulado += evento["chance"]
        if rolagem <= acumulado:
            cidade.aplicar_efeitos(evento["efeitos"])
            cidade.evento_ativo = {
                "titulo": evento["titulo"],
                "descricao": evento["descricao"],
                "efeitos": evento["efeitos"],
            }
            return cidade.evento_ativo

    cidade.evento_ativo = None
    return None

