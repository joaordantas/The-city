from .dados import CONSTRUCOES


def listar_construcoes():
    return [
        {"id": construcao_id, **dados}
        for construcao_id, dados in CONSTRUCOES.items()
    ]


def construir(cidade, construcao_id, posicao=None):
    if construcao_id not in CONSTRUCOES:
        return False, "Construcao desconhecida."

    construcao = CONSTRUCOES[construcao_id]
    custo = construcao["custo"]

    if cidade.dados["dinheiro"] < custo:
        return False, "Dinheiro insuficiente para construir."

    if posicao is None:
        posicao = encontrar_posicao_livre(cidade)

    if posicao is None:
        return False, "O mapa esta cheio."

    if posicao < 0 or posicao >= len(cidade.mapa):
        return False, "Posicao invalida no mapa."

    if cidade.mapa[posicao] is not None:
        return False, "Esse espaco do mapa ja esta ocupado."

    cidade.dados["dinheiro"] -= custo
    cidade.construcoes.append(construcao_id)
    cidade.mapa[posicao] = construcao_id

    efeitos = {
        chave: valor
        for chave, valor in construcao.items()
        if chave in cidade.dados and isinstance(valor, (int, float))
    }
    cidade.aplicar_efeitos(efeitos)

    return True, f"{construcao['nome']} construida com sucesso."


def encontrar_posicao_livre(cidade):
    for indice, valor in enumerate(cidade.mapa):
        if valor is None:
            return indice
    return None

