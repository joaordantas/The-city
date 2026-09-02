from .dados import CONFIG_CRISES
from .progressao import comparar


def _valor_crise(cidade, campo):
    if campo == "maior_utilizacao":
        return max(cidade.dados["agua"], cidade.dados["energia"])
    return cidade.dados[campo]


def atualizar_crises(cidade):
    if cidade.simulacao_suja:
        cidade.recalcular_simulacao()
    alertas = []
    recuperadas = []
    limite = CONFIG_CRISES["rodadas_para_derrota"]

    for crise_id, config in CONFIG_CRISES["tipos"].items():
        atual = _valor_crise(cidade, config["campo"])
        ativa = comparar(atual, config["operador"], config["valor"])
        anterior = cidade.contadores_crise.get(crise_id, 0)
        if ativa:
            cidade.contadores_crise[crise_id] = anterior + 1
            restante = max(0, limite - cidade.contadores_crise[crise_id])
            alertas.append({
                "id": crise_id,
                "titulo": config["titulo"],
                "rodadas": cidade.contadores_crise[crise_id],
                "restantes": restante,
                "valor_atual": atual,
            })
        else:
            if anterior:
                recuperadas.append({"id": crise_id, "titulo": config["titulo"]})
                cidade.crises_resolvidas += 1
                cidade.registrar_historico("crise", f"{config['titulo']} superada", "A cidade saiu da faixa critica.")
            cidade.contadores_crise[crise_id] = 0

    cidade.rodadas_em_crise = max(cidade.contadores_crise.values(), default=0)
    fatal = next((alerta for alerta in alertas if alerta["rodadas"] >= limite), None)
    if fatal:
        cidade.status = "derrota"
        cidade.motivo_fim = fatal["titulo"]
    cidade.crises_ativas = alertas
    return {"ativas": alertas, "recuperadas": recuperadas, "fatal": fatal}


def resumo_crises(cidade):
    return {
        "ativas": cidade.crises_ativas,
        "contadores": cidade.contadores_crise.copy(),
        "resolvidas": cidade.crises_resolvidas,
        "rodadas_para_derrota": CONFIG_CRISES["rodadas_para_derrota"],
    }
