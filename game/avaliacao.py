from .dados import CONFIG_AVALIACAO, MISSOES
from .progressao import avaliar_plano_governo


def _limitar(valor, minimo=0, maximo=1000):
    return round(max(minimo, min(maximo, valor)))


def _media(historico, campo, padrao):
    valores = [item[campo] for item in historico if campo in item]
    return sum(valores) / len(valores) if valores else padrao


def calcular_avaliacao(cidade):
    if cidade.simulacao_suja:
        cidade.recalcular_simulacao()
    historico = cidade.historico_metricas
    plano = avaliar_plano_governo(cidade)
    saldo = cidade.dados["dinheiro"]
    media_resultado = _media(historico, "resultado", cidade.ultimo_resultado or 0)
    nota_saldo = _limitar(500 + saldo / 20)
    nota_resultado = _limitar(500 + media_resultado / 3)

    areas = {
        "economia": _limitar(nota_saldo * 0.45 + nota_resultado * 0.55),
        "saude": _limitar(_media(historico, "saude", cidade.dados["saude"]) * 10),
        "educacao": _limitar(_media(historico, "educacao", cidade.dados["educacao"]) * 10),
        "emprego": _limitar((100 - _media(historico, "taxa_desemprego", cidade.simulacao["trabalho"]["taxa_desemprego"])) * 10),
        "ambiente": _limitar((100 - _media(historico, "poluicao", cidade.dados["poluicao"])) * 10),
        "qualidade": _limitar(_media(historico, "qualidade_vida", cidade.dados["qualidade_vida"]) * 10),
        "gestao": _limitar(
            (len(cidade.missoes_concluidas) / max(1, len(MISSOES))) * 600
            + (plano["percentual"] / 100) * 300
            + min(100, cidade.crises_resolvidas * 50)
        ),
    }
    pesos = CONFIG_AVALIACAO["pesos"]
    total = round(sum(areas[nome] * pesos[nome] for nome in areas))
    maximo = 1000 * sum(pesos.values())
    classificacao = next(
        item["nome"] for item in CONFIG_AVALIACAO["classificacoes"]
        if total >= item["minimo"]
    )
    return {
        "areas": areas,
        "pesos": pesos.copy(),
        "total": total,
        "maximo": maximo,
        "classificacao": classificacao,
        "plano_governo": plano,
        "formula": "Cada area vale 0-1000; o total aplica os pesos configurados. Economia combina saldo final e media dos resultados.",
    }
