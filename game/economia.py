from .dados import CONFIG_IMPOSTOS, CONFIG_SIMULACAO
from .producao import processar_producao


def calcular_economia(cidade):
    if cidade.simulacao_suja:
        cidade.recalcular_simulacao()

    trabalho = cidade.simulacao["trabalho"]
    fator_mao_obra = min(1, trabalho["empregados"] / cidade.dados["empregos"]) if cidade.dados["empregos"] else 1
    atividade_comercio = sum(
        predio["atividade_efetiva"] for predio in cidade.simulacao["predios"]
        if predio["categoria"] == "comercio"
    )
    atividade_comercio *= cidade.fatores_producao["comercio"]
    atividade_industria = sum(
        predio["atividade_efetiva"] for predio in cidade.simulacao["predios"]
        if predio["categoria"] == "industria"
    )
    receitas_detalhes = {
        "IPTU / Residencial": round(cidade.dados["populacao"] * CONFIG_IMPOSTOS["base_residencial_por_habitante"] * cidade.impostos["residencial"] / 100),
        "Comercio": round(atividade_comercio * fator_mao_obra * cidade.impostos["comercio"] / 100),
        "Industria": round(atividade_industria * fator_mao_obra * cidade.impostos["industria"] / 100),
        "Outras receitas": CONFIG_IMPOSTOS["outras_receitas"],
    }
    fator_receitas = max(0, 1 + cidade.valor_modificador("receitas_pct") / 100)
    if fator_receitas != 1:
        receitas_detalhes = {nome: round(valor * fator_receitas) for nome, valor in receitas_detalhes.items()}
    receitas = sum(receitas_detalhes.values())

    custo_servicos = round(cidade.dados["populacao"] * CONFIG_SIMULACAO["custo_servicos_por_habitante"])
    despesas_detalhes = {
        "Saude": round(custo_servicos * 0.30),
        "Educacao": round(custo_servicos * 0.25),
        "Agua": round(custo_servicos * 0.15),
        "Energia": round(custo_servicos * 0.15),
        "Infraestrutura": 0,
        "Outras despesas": round(custo_servicos * 0.15),
    }
    manutencao = 0
    for predio in cidade.simulacao["predios"]:
        valor = predio["manutencao"]
        manutencao += valor
        grupo = {
            "saude": "Saude",
            "educacao": "Educacao",
            "infraestrutura": "Agua",
            "ambiental": "Energia",
        }.get(predio["categoria"], "Infraestrutura")
        despesas_detalhes[grupo] += valor

    fator_despesas = max(0, 1 + cidade.valor_modificador("despesas_pct") / 100)
    if fator_despesas != 1:
        despesas_detalhes = {nome: round(valor * fator_despesas) for nome, valor in despesas_detalhes.items()}

    despesas = sum(despesas_detalhes.values())
    return {
        **trabalho,
        "atividade_economica": atividade_comercio + atividade_industria,
        "receitas_detalhes": receitas_detalhes,
        "despesas_detalhes": despesas_detalhes,
        "receitas": receitas,
        "despesas": despesas,
        "manutencao": manutencao,
        "servicos_publicos": custo_servicos,
        "resultado": receitas - despesas,
        "previsao": receitas - despesas,
    }


def processar_rodada(cidade):
    rodada_processada = cidade.dados["rodada"]
    cidade.recalcular_simulacao()
    producao = processar_producao(cidade)
    resumo = calcular_economia(cidade)
    cidade.dados["dinheiro"] += resumo["resultado"]
    cidade.ultimo_resultado = resumo["resultado"]
    resumo["crescimento_populacao"] = cidade.processar_populacao()
    cidade.recalcular_simulacao()
    resumo["dinheiro_final"] = cidade.dados["dinheiro"]
    resumo["rodada"] = rodada_processada
    resumo["producao"] = producao
    return resumo
