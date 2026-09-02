from copy import deepcopy

from .dados import CONFIG_MAPA


def setor_da_posicao(posicao):
    for setor_id, setor in CONFIG_MAPA["setores"].items():
        if posicao in setor["celulas"]:
            return setor_id
    return None


def posicao_desbloqueada(cidade, posicao):
    setor_id = setor_da_posicao(posicao)
    return setor_id in cidade.setores_desbloqueados


def vizinhos(posicao):
    colunas = CONFIG_MAPA["colunas"]
    total = CONFIG_MAPA["total_celulas"]
    linha, coluna = divmod(posicao, colunas)
    candidatos = []
    if coluna > 0:
        candidatos.append(posicao - 1)
    if coluna < colunas - 1:
        candidatos.append(posicao + 1)
    if linha > 0:
        candidatos.append(posicao - colunas)
    if posicao + colunas < total:
        candidatos.append(posicao + colunas)
    return candidatos


def possui_acesso_viario(cidade, posicao):
    colunas = CONFIG_MAPA["colunas"]
    linhas = CONFIG_MAPA["total_celulas"] // colunas
    linha, coluna = divmod(posicao, colunas)
    if linha in (0, linhas - 1) or coluna in (0, colunas - 1):
        return True
    return any(vizinho in cidade.estradas for vizinho in vizinhos(posicao))


def desbloquear_setor(cidade, setor_id):
    setor = CONFIG_MAPA["setores"].get(setor_id)
    if not setor or setor_id == CONFIG_MAPA["setor_inicial"]:
        return False, "Setor invalido para expansao."
    if cidade.dados["rodada"] < 6:
        return False, "A expansao territorial sera liberada na rodada 6."
    if setor_id in cidade.setores_desbloqueados:
        return False, "Este setor ja foi desbloqueado."
    if cidade.dados["dinheiro"] < setor["custo"]:
        falta = setor["custo"] - cidade.dados["dinheiro"]
        return False, f"Dinheiro insuficiente para expandir. Faltam R$ {falta}."
    cidade.dados["dinheiro"] -= setor["custo"]
    cidade.setores_desbloqueados.add(setor_id)
    cidade.registrar_historico("expansao", f"{setor['nome']} desbloqueado", f"A cidade investiu R$ {setor['custo']} em novo territorio.")
    return True, f"{setor['nome']} desbloqueado por R$ {setor['custo']}."


def remover_obstaculo(cidade, posicao):
    if not posicao_desbloqueada(cidade, posicao):
        return False, "Desbloqueie este setor antes de limpar o terreno."
    obstaculo = cidade.obstaculos.get(posicao)
    if not obstaculo:
        return False, "Nao existe obstaculo neste terreno."
    custo = obstaculo["custo_remocao"]
    if cidade.dados["dinheiro"] < custo:
        return False, f"Dinheiro insuficiente. Faltam R$ {custo - cidade.dados['dinheiro']}."
    cidade.dados["dinheiro"] -= custo
    del cidade.obstaculos[posicao]
    return True, f"{obstaculo['nome']} removido por R$ {custo}."


def construir_estrada(cidade, posicao):
    if cidade.dados["rodada"] < 3:
        return False, "Estradas serao liberadas na rodada 3."
    if not isinstance(posicao, int) or isinstance(posicao, bool) or posicao < 0 or posicao >= len(cidade.mapa):
        return False, "Posicao invalida no mapa."
    if not posicao_desbloqueada(cidade, posicao):
        return False, "Este terreno pertence a um setor bloqueado."
    if cidade.mapa[posicao] is not None or posicao in cidade.obstaculos:
        return False, "Nao e possivel construir estrada nesta area."
    if posicao in cidade.estradas:
        return False, "Ja existe uma estrada nesta area."
    custo = CONFIG_MAPA["custo_estrada"]
    if cidade.dados["dinheiro"] < custo:
        return False, f"Dinheiro insuficiente. Faltam R$ {custo - cidade.dados['dinheiro']}."
    cidade.dados["dinheiro"] -= custo
    cidade.estradas.add(posicao)
    cidade.marcar_simulacao_suja()
    return True, f"Estrada construida por R$ {custo}."


def calcular_transito(cidade):
    capacidade = CONFIG_MAPA["capacidade_viaria_base"] + len(cidade.estradas) * CONFIG_MAPA["capacidade_por_estrada"]
    demanda = round(cidade.dados["populacao"] * CONFIG_MAPA["demanda_por_habitante"] + len(cidade.construcoes) * 2)
    utilizacao = round(demanda / capacidade * 100) if capacidade else 999
    return {
        "capacidade": capacidade,
        "demanda": demanda,
        "utilizacao": utilizacao,
        "estado": "Congestionado" if utilizacao > 100 else "Atencao" if utilizacao >= 80 else "Fluindo",
    }


def resumo_territorio(cidade):
    celulas = []
    for posicao in range(CONFIG_MAPA["total_celulas"]):
        setor_id = setor_da_posicao(posicao)
        setor = CONFIG_MAPA["setores"][setor_id]
        celulas.append({
            "posicao": posicao,
            "setor_id": setor_id,
            "setor": setor["nome"],
            "distrito": setor["distrito"],
            "desbloqueada": setor_id in cidade.setores_desbloqueados,
            "obstaculo": deepcopy(cidade.obstaculos.get(posicao)),
            "estrada": posicao in cidade.estradas,
        })
    setores = [
        {"id": setor_id, **deepcopy(setor), "desbloqueado": setor_id in cidade.setores_desbloqueados}
        for setor_id, setor in CONFIG_MAPA["setores"].items()
    ]
    return {"colunas": CONFIG_MAPA["colunas"], "celulas": celulas, "setores": setores, "transito": calcular_transito(cidade), "custo_estrada": CONFIG_MAPA["custo_estrada"]}
