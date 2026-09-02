from copy import deepcopy

from .dados import PEDIDOS_LOGISTICOS


def atualizar_pedido(cidade):
    if cidade.pedido_ativo:
        return cidade.pedido_ativo
    rodada = cidade.dados["rodada"]
    pedido = next((
        item for item in PEDIDOS_LOGISTICOS
        if item["id"] not in cidade.pedidos_finalizados
        and item["rodada_inicio"] <= rodada <= item["rodada_fim"]
    ), None)
    if pedido:
        cidade.pedido_ativo = deepcopy(pedido)
        cidade.registrar_historico("logistica", f"Novo pedido: {pedido['titulo']}", "Decida entre entregar o estoque ou guardar os recursos.")
    return cidade.pedido_ativo


def entregar_pedido(cidade):
    pedido = cidade.pedido_ativo
    if not pedido:
        return False, "Nao existe pedido logistico ativo."
    faltas = {
        recurso: quantidade - cidade.estoque.get(recurso, 0)
        for recurso, quantidade in pedido["recursos"].items()
        if cidade.estoque.get(recurso, 0) < quantidade
    }
    if faltas:
        texto = ", ".join(f"{quantidade} {recurso}" for recurso, quantidade in faltas.items())
        return False, f"Estoque insuficiente. Faltam {texto}."
    for recurso, quantidade in pedido["recursos"].items():
        cidade.estoque[recurso] -= quantidade
    cidade.dados["dinheiro"] += pedido["recompensa"]
    cidade.pedidos_finalizados.add(pedido["id"])
    cidade.pedido_ativo = None
    cidade.registrar_historico("logistica", "Pedido entregue", f"Recompensa recebida: R$ {pedido['recompensa']}.")
    return True, f"Pedido entregue. +R$ {pedido['recompensa']}."


def recusar_pedido(cidade):
    if not cidade.pedido_ativo:
        return False, "Nao existe pedido logistico ativo."
    pedido = cidade.pedido_ativo
    cidade.pedidos_finalizados.add(pedido["id"])
    cidade.pedido_ativo = None
    cidade.registrar_historico("logistica", "Pedido recusado", "Os recursos permaneceram no estoque da cidade.")
    return True, "Pedido recusado. O estoque foi preservado."


def resumo_logistica(cidade):
    return {"pedido_ativo": deepcopy(cidade.pedido_ativo), "finalizados": sorted(cidade.pedidos_finalizados)}
