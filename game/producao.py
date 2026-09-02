from copy import deepcopy

from .dados import CONFIG_PRODUCAO


def capacidade_estoque(cidade):
    if cidade.simulacao_suja:
        cidade.recalcular_simulacao()
    adicional = sum(predio.get("capacidade_estoque", 0) for predio in cidade.simulacao["predios"])
    return CONFIG_PRODUCAO["capacidade_base"] + adicional


def prever_producao(cidade):
    if cidade.simulacao_suja:
        cidade.recalcular_simulacao()
    produzido = {recurso: 0 for recurso in CONFIG_PRODUCAO["recursos"]}
    demanda_mercadorias = 0
    for predio in cidade.simulacao["predios"]:
        fator = predio["eficiencia"] / 100
        for recurso, valor in predio.get("producao", {}).items():
            produzido[recurso] += round(valor * fator)
        demanda_mercadorias += round(predio.get("consumo_estoque", {}).get("mercadorias", 0) * fator)
    demanda_alimentos = round(cidade.dados["populacao"] * CONFIG_PRODUCAO["demanda_alimentos_por_habitante"])
    return {
        "produzido": produzido,
        "demanda_mercadorias": demanda_mercadorias,
        "demanda_alimentos": demanda_alimentos,
    }


def processar_producao(cidade):
    previsao = prever_producao(cidade)
    capacidade = capacidade_estoque(cidade)
    descartado = {recurso: 0 for recurso in CONFIG_PRODUCAO["recursos"]}
    for recurso, quantidade in previsao["produzido"].items():
        espaco = max(0, capacidade - cidade.estoque[recurso])
        armazenado = min(espaco, quantidade)
        cidade.estoque[recurso] += armazenado
        descartado[recurso] = quantidade - armazenado

    demanda_mercadorias = previsao["demanda_mercadorias"]
    consumidas = min(cidade.estoque["mercadorias"], demanda_mercadorias)
    cidade.estoque["mercadorias"] -= consumidas
    fator_comercio = consumidas / demanda_mercadorias if demanda_mercadorias else 1
    if demanda_mercadorias:
        fator_comercio = max(CONFIG_PRODUCAO["fator_minimo_comercio"], fator_comercio)

    demanda_alimentos = previsao["demanda_alimentos"]
    externo = CONFIG_PRODUCAO["abastecimento_externo_alimentos"]
    necessario_estoque = max(0, demanda_alimentos - externo)
    alimentos = min(cidade.estoque["alimentos"], necessario_estoque)
    cidade.estoque["alimentos"] -= alimentos
    atendido = min(demanda_alimentos, externo + alimentos)
    fator_alimentos = atendido / demanda_alimentos if demanda_alimentos else 1
    cidade.fatores_producao = {"comercio": fator_comercio, "alimentos": fator_alimentos}
    cidade.marcar_simulacao_suja()
    return {
        **previsao,
        "descartado": descartado,
        "consumido": {"mercadorias": consumidas, "alimentos": alimentos},
        "fatores": deepcopy(cidade.fatores_producao),
        "capacidade": capacidade,
    }


def resumo_producao(cidade):
    previsao = prever_producao(cidade)
    return {
        "estoque": deepcopy(cidade.estoque),
        "capacidade": capacidade_estoque(cidade),
        "previsao": previsao,
        "fatores_ultima_rodada": deepcopy(cidade.fatores_producao),
    }
