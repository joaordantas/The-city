from .dados import CONFIG_PROGRESSAO, CONSTRUCOES, PLANO_GOVERNO


def comparar(atual, operador, alvo):
    operacoes = {
        ">=": lambda: atual >= alvo,
        "<=": lambda: atual <= alvo,
        ">": lambda: atual > alvo,
        "<": lambda: atual < alvo,
        "==": lambda: atual == alvo,
    }
    return operacoes[operador]()


def obter_fase(rodada):
    return next(fase for fase in CONFIG_PROGRESSAO["fases"] if fase["inicio"] <= rodada <= fase["fim"])


def sistema_desbloqueado(nome, rodada):
    return rodada >= CONFIG_PROGRESSAO["sistemas"][nome]


def obter_progressao(rodada):
    fase = obter_fase(rodada)
    sistemas = {
        nome: {"desbloqueado": sistema_desbloqueado(nome, rodada), "rodada": inicio}
        for nome, inicio in CONFIG_PROGRESSAO["sistemas"].items()
    }
    construcoes = [
        {"id": tipo, "nome": dados["nome"], "rodada": dados["rodada_desbloqueio"]}
        for tipo, dados in CONSTRUCOES.items()
    ]
    return {"fase": fase, "sistemas": sistemas, "construcoes": construcoes}


def listar_desbloqueios(rodada_anterior, rodada_atual):
    novos = []
    for tipo, dados in CONSTRUCOES.items():
        if rodada_anterior < dados["rodada_desbloqueio"] <= rodada_atual:
            novos.append({"tipo": "construcao", "id": tipo, "titulo": dados["nome"]})
    for nome, inicio in CONFIG_PROGRESSAO["sistemas"].items():
        if rodada_anterior < inicio <= rodada_atual and nome not in ("missoes", "prefeitura"):
            novos.append({"tipo": "sistema", "id": nome, "titulo": nome.capitalize()})
    return novos


def avaliar_plano_governo(cidade):
    itens = []
    for objetivo in PLANO_GOVERNO:
        atual = cidade.dados[objetivo["campo"]]
        concluido = comparar(atual, objetivo["operador"], objetivo["valor"])
        itens.append({**objetivo, "atual": atual, "concluido": concluido})
    concluidos = sum(item["concluido"] for item in itens)
    return {
        "itens": itens,
        "concluidos": concluidos,
        "total": len(itens),
        "percentual": round(concluidos / len(itens) * 100) if itens else 0,
    }
