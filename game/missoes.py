from copy import deepcopy

from .dados import MISSOES


MAX_MISSOES_VISIVEIS = 3


def _valor_missao(cidade, missao):
    alvo = missao["alvo"]
    tipo = missao["tipo"]
    if cidade.simulacao_suja:
        cidade.recalcular_simulacao()

    if tipo == "construcao":
        return sum(predio["tipo"] == alvo["tipo"] for predio in cidade.construcoes)
    if tipo in ("populacao", "empregos"):
        return cidade.dados[tipo]
    if tipo in ("indicador", "servico"):
        return cidade.dados[alvo["campo"]]
    if tipo == "infraestrutura":
        return cidade.dados[alvo["recurso"]]
    if tipo == "saldo_positivo":
        return cidade.ultimo_resultado or 0
    if tipo == "poluicao":
        return cidade.dados["poluicao"]
    if tipo == "eficiencia":
        eficiencias = [predio["eficiencia"] for predio in cidade.simulacao["predios"]]
        return min(eficiencias) if eficiencias else 0
    if tipo == "sobreviver_crise":
        return cidade.crises_resolvidas
    return 0


def _cumprida(missao, atual):
    tipo = missao["tipo"]
    alvo = missao["alvo"]["valor"]
    if tipo in ("indicador",):
        return atual <= alvo if missao["alvo"].get("operador") == "<=" else atual >= alvo
    if tipo in ("infraestrutura", "poluicao"):
        return atual <= alvo
    return atual >= alvo


def listar_missoes(cidade):
    rodada = cidade.dados["rodada"]
    candidatas = [
        missao for missao in MISSOES
        if missao["id"] not in cidade.missoes_concluidas
        and missao["rodada_inicio"] <= rodada <= missao["rodada_fim"]
    ][:MAX_MISSOES_VISIVEIS]

    resultado = []
    for missao in candidatas:
        atual = _valor_missao(cidade, missao)
        resultado.append({
            **deepcopy(missao),
            "atual": atual,
            "cumprida": _cumprida(missao, atual),
        })
    return resultado


def avaliar_missoes(cidade):
    concluidas_agora = []
    for missao in listar_missoes(cidade):
        if not missao["cumprida"] or missao["id"] in cidade.missoes_concluidas:
            continue
        recompensa = missao["recompensa"]
        cidade.missoes_concluidas.add(missao["id"])
        cidade.dados["dinheiro"] += recompensa.get("dinheiro", 0)
        cidade.pontos_progresso += recompensa.get("progresso", 0)
        cidade.registrar_historico(
            "missao",
            f"Missao concluida: {missao['titulo']}",
            f"Recompensa: R$ {recompensa.get('dinheiro', 0)} e {recompensa.get('progresso', 0)} pontos.",
        )
        concluidas_agora.append(missao)
    return concluidas_agora


def resumo_missoes(cidade):
    return {
        "ativas": listar_missoes(cidade),
        "concluidas": sorted(cidade.missoes_concluidas),
        "total_concluidas": len(cidade.missoes_concluidas),
        "total": len(MISSOES),
        "pontos_progresso": cidade.pontos_progresso,
        "max_visiveis": MAX_MISSOES_VISIVEIS,
    }
