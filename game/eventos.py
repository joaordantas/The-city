import random
from copy import deepcopy

from .dados import EVENTOS
from .progressao import comparar, obter_fase


def _buscar_evento(evento_id):
    return next((evento for evento in EVENTOS if evento["id"] == evento_id), None)


def _valor_condicao(cidade, campo):
    if cidade.simulacao_suja:
        cidade.recalcular_simulacao()
    if campo == "taxa_desemprego":
        return cidade.simulacao["trabalho"]["taxa_desemprego"]
    return cidade.dados.get(campo)


def _condicoes_atendidas(cidade, evento):
    return all(
        comparar(_valor_condicao(cidade, item["campo"]), item["operador"], item["valor"])
        for item in evento.get("condicoes", [])
    )


def _em_cooldown(cidade, evento):
    ultima = cidade.eventos_ocorridos.get(evento["id"])
    return ultima is not None and cidade.dados["rodada"] - ultima < evento.get("cooldown", 0)


def iniciar_evento(cidade, evento_id):
    evento = _buscar_evento(evento_id)
    if not evento:
        return None
    cidade.eventos_ocorridos[evento_id] = cidade.dados["rodada"]
    cidade.evento_ativo = {
        "id": evento["id"],
        "titulo": evento["titulo"],
        "descricao": evento["descricao"],
        "escolhas": deepcopy(evento["escolhas"]),
        "rodada_limite": cidade.dados["rodada"],
        "aviso": "Se voce nao escolher ate o fim da rodada, a consequencia de omissao sera aplicada.",
    }
    cidade.registrar_historico("evento", f"Evento: {evento['titulo']}", "Uma decisao ficou pendente.")
    return deepcopy(cidade.evento_ativo)


def sortear_evento(cidade, rng=random):
    if cidade.evento_ativo or cidade.status != "jogando":
        return deepcopy(cidade.evento_ativo)
    rodada = cidade.dados["rodada"]
    intensidade = obter_fase(rodada)["intensidade_eventos"]
    if intensidade <= 0:
        return None

    possiveis = []
    for evento in EVENTOS:
        if rodada < evento["rodada_inicio"] or _em_cooldown(cidade, evento):
            continue
        if not _condicoes_atendidas(cidade, evento):
            continue
        if rng.random() * 100 <= evento["chance"] * intensidade:
            possiveis.append(evento)
    if not possiveis:
        return None
    return iniciar_evento(cidade, rng.choice(possiveis)["id"])


def aplicar_efeitos(cidade, efeitos, origem):
    aplicados = []
    for efeito in efeitos:
        tipo = efeito["tipo"]
        if tipo == "dinheiro":
            cidade.dados["dinheiro"] += efeito["valor"]
            aplicados.append({"tipo": tipo, "valor": efeito["valor"]})
        elif tipo == "modificador":
            modificador = {
                "id": f"mod-{cidade.proximo_modificador_id}",
                "origem": origem,
                "nome": efeito["nome"],
                "alvo": efeito["alvo"],
                "valor": efeito["valor"],
                "rodadas_restantes": efeito["duracao"],
            }
            cidade.proximo_modificador_id += 1
            cidade.modificadores.append(modificador)
            aplicados.append(deepcopy(modificador))
        elif tipo == "futuro":
            consequencia = {
                "id": f"futuro-{cidade.proxima_consequencia_id}",
                "origem": origem,
                "titulo": efeito["titulo"],
                "rodadas_restantes": efeito["apos_rodadas"],
                "efeitos": deepcopy(efeito["efeitos"]),
            }
            cidade.proxima_consequencia_id += 1
            cidade.consequencias_futuras.append(consequencia)
            aplicados.append(deepcopy(consequencia))
    cidade.marcar_simulacao_suja()
    cidade.limitar_indicadores()
    return aplicados


def responder_evento(cidade, escolha_id):
    if not cidade.evento_ativo:
        return False, "Nao existe evento aguardando decisao.", []
    evento = _buscar_evento(cidade.evento_ativo["id"])
    escolha = next((item for item in evento["escolhas"] if item["id"] == escolha_id), None)
    if not escolha:
        return False, "Escolha invalida para este evento.", []
    aplicados = aplicar_efeitos(cidade, escolha["efeitos"], evento["titulo"])
    cidade.registrar_historico("decisao", escolha["titulo"], escolha["descricao"])
    cidade.evento_ativo = None
    return True, f"Decisao tomada: {escolha['titulo']}.", aplicados


def resolver_evento_ignorado(cidade):
    if not cidade.evento_ativo:
        return None
    evento = _buscar_evento(cidade.evento_ativo["id"])
    aplicados = aplicar_efeitos(cidade, evento["ignorado"], evento["titulo"])
    resultado = {"id": evento["id"], "titulo": evento["titulo"], "efeitos": aplicados}
    cidade.registrar_historico(
        "omissao",
        f"Evento ignorado: {evento['titulo']}",
        "A consequencia automatica foi aplicada no fim da rodada.",
    )
    cidade.evento_ativo = None
    return resultado


def processar_consequencias_futuras(cidade):
    aplicadas = []
    pendentes = []
    for consequencia in cidade.consequencias_futuras:
        consequencia["rodadas_restantes"] -= 1
        if consequencia["rodadas_restantes"] <= 0:
            efeitos = aplicar_efeitos(cidade, consequencia["efeitos"], consequencia["origem"])
            aplicadas.append({**consequencia, "efeitos_aplicados": efeitos})
            cidade.registrar_historico("consequencia", consequencia["titulo"], "A consequencia prevista aconteceu.")
        else:
            pendentes.append(consequencia)
    cidade.consequencias_futuras = pendentes
    return aplicadas


def avancar_modificadores(cidade):
    expirados = []
    ativos = []
    for modificador in cidade.modificadores:
        modificador["rodadas_restantes"] -= 1
        if modificador["rodadas_restantes"] <= 0:
            expirados.append(deepcopy(modificador))
        else:
            ativos.append(modificador)
    cidade.modificadores = ativos
    if expirados:
        cidade.marcar_simulacao_suja()
    return expirados
