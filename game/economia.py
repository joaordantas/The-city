from .dados import CONSTRUCOES, REGRAS_ECONOMIA


def calcular_economia(cidade):
    trabalhadores = min(cidade.dados["populacao"], cidade.dados["empregos"])
    desempregados = max(0, cidade.dados["populacao"] - cidade.dados["empregos"])

    producao_base = trabalhadores * REGRAS_ECONOMIA["producao_por_trabalhador"]
    producao_construcoes = sum(
        CONSTRUCOES[construcao_id].get("atividade_economica", 0)
        for construcao_id in cidade.construcoes
    )

    bonus_educacao = cidade.dados["educacao"] * REGRAS_ECONOMIA["bonus_qualidade_por_educacao"]
    atividade_economica = int((producao_base + producao_construcoes) * (1 + bonus_educacao / 100))
    impostos = int(atividade_economica * REGRAS_ECONOMIA["aliquota_impostos"])

    custo_servicos = int(cidade.dados["populacao"] * REGRAS_ECONOMIA["custo_servicos_por_habitante"])
    manutencao = sum(
        CONSTRUCOES[construcao_id].get("manutencao", 0)
        for construcao_id in cidade.construcoes
    )
    despesas = custo_servicos + manutencao
    resultado = impostos - despesas

    return {
        "trabalhadores": trabalhadores,
        "desempregados": desempregados,
        "atividade_economica": atividade_economica,
        "receitas": impostos,
        "despesas": despesas,
        "manutencao": manutencao,
        "servicos_publicos": custo_servicos,
        "resultado": resultado,
    }


def processar_rodada(cidade):
    resumo = calcular_economia(cidade)
    cidade.dados["dinheiro"] += resumo["resultado"]

    atualizar_populacao(cidade, resumo)
    atualizar_qualidade_vida(cidade, resumo)
    atualizar_crise_financeira(cidade)

    cidade.dados["rodada"] += 1
    cidade.limitar_indicadores()

    resumo["dinheiro_final"] = cidade.dados["dinheiro"]
    resumo["rodada"] = cidade.dados["rodada"] - 1
    return resumo


def atualizar_populacao(cidade, resumo):
    if cidade.dados["populacao"] >= cidade.dados["capacidade_populacional"]:
        return

    crescimento = REGRAS_ECONOMIA["crescimento_populacional_base"]

    if cidade.dados["qualidade_vida"] >= 70:
        crescimento += 3
    elif cidade.dados["qualidade_vida"] < 35:
        crescimento -= 2

    if resumo["desempregados"] > cidade.dados["populacao"] * 0.35:
        crescimento -= 2

    crescimento = max(-3, crescimento)
    nova_populacao = cidade.dados["populacao"] + crescimento
    cidade.dados["populacao"] = min(nova_populacao, cidade.dados["capacidade_populacional"])


def atualizar_qualidade_vida(cidade, resumo):
    variacao = 0
    variacao += (cidade.dados["educacao"] - 50) * 0.015
    variacao += (cidade.dados["saude"] - 50) * 0.018
    variacao -= cidade.dados["poluicao"] * REGRAS_ECONOMIA["penalidade_qualidade_por_poluicao"]

    if cidade.dados["energia"] < REGRAS_ECONOMIA["limite_alerta_recurso"]:
        variacao -= 2
    if cidade.dados["agua"] < REGRAS_ECONOMIA["limite_alerta_recurso"]:
        variacao -= 2
    if resumo["desempregados"] > cidade.dados["populacao"] * 0.25:
        variacao -= 1

    cidade.dados["qualidade_vida"] += round(variacao)


def atualizar_crise_financeira(cidade):
    if cidade.dados["dinheiro"] < 0:
        cidade.rodadas_em_crise += 1
    else:
        cidade.rodadas_em_crise = 0

    if cidade.rodadas_em_crise >= REGRAS_ECONOMIA["rodadas_em_crise_para_derrota"]:
        cidade.status = "falencia"
    elif cidade.dados["rodada"] >= cidade.dados["max_rodadas"]:
        cidade.status = "concluido"

