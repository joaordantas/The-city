from .dados import (
    CATEGORIAS_CONSTRUCOES,
    CONFIG_SIMULACAO,
    CONSTRUCOES,
    dados_construcao_nivel,
)
from .progressao import sistema_desbloqueado
from .territorio import posicao_desbloqueada


def listar_construcoes(rodada=None):
    return [
        {
            "id": tipo,
            **dados_construcao_nivel(tipo, 1),
            "tamanho": {"largura": 1, "altura": 1},
            "desbloqueada": rodada is None or CONSTRUCOES[tipo]["rodada_desbloqueio"] <= rodada,
        }
        for tipo in CONSTRUCOES
    ]


def listar_categorias(rodada=None):
    usadas = {dados["categoria"] for dados in CONSTRUCOES.values()}
    return [
        {
            "id": categoria,
            "nome": nome,
            "desbloqueada": rodada is None or any(
                dados["categoria"] == categoria and dados["rodada_desbloqueio"] <= rodada
                for dados in CONSTRUCOES.values()
            ),
        }
        for categoria, nome in CATEGORIAS_CONSTRUCOES.items()
        if categoria in usadas
    ]


def construir(cidade, tipo, posicao):
    if tipo not in CONSTRUCOES:
        return False, "Construcao desconhecida.", None
    desbloqueio = CONSTRUCOES[tipo]["rodada_desbloqueio"]
    if cidade.dados["rodada"] < desbloqueio:
        return False, f"{CONSTRUCOES[tipo]['nome']} sera desbloqueada na rodada {desbloqueio}.", None
    erro = validar_posicao(cidade, posicao)
    if erro:
        return False, erro, None

    dados = CONSTRUCOES[tipo]
    limite = dados.get("limite")
    if limite is not None:
        quantidade = sum(predio["tipo"] == tipo for predio in cidade.construcoes)
        if quantidade >= limite:
            return False, f"Limite de {limite} para {dados['nome']} atingido.", None
    if cidade.dados["dinheiro"] < dados["custo"]:
        falta = dados["custo"] - cidade.dados["dinheiro"]
        return False, f"Dinheiro insuficiente. Faltam R$ {falta}.", None

    uid = f"predio-{cidade.proximo_predio_id}"
    cidade.proximo_predio_id += 1
    predio = {"id": uid, "tipo": tipo, "nivel": 1, "posicao": posicao, "investimento": dados["custo"]}
    cidade.dados["dinheiro"] -= dados["custo"]
    cidade.construcoes.append(predio)
    cidade.mapa[posicao] = uid
    cidade.marcar_simulacao_suja()
    return True, f"{dados['nome']} construida por R$ {dados['custo']}.", uid


def mover(cidade, predio_id, nova_posicao):
    predio = encontrar_predio(cidade, predio_id)
    if not predio:
        return False, "Predio nao encontrado."
    erro = validar_posicao(cidade, nova_posicao)
    if erro:
        return False, erro
    cidade.mapa[predio["posicao"]] = None
    cidade.mapa[nova_posicao] = predio_id
    predio["posicao"] = nova_posicao
    cidade.marcar_simulacao_suja()
    return True, "Predio movido sem custo e sem alterar seus efeitos."


def demolir(cidade, predio_id):
    predio = encontrar_predio(cidade, predio_id)
    if not predio:
        return False, "Predio nao encontrado.", 0
    reembolso = round(predio["investimento"] * CONFIG_SIMULACAO["reembolso_demolicao"])
    cidade.dados["dinheiro"] += reembolso
    cidade.mapa[predio["posicao"]] = None
    cidade.construcoes.remove(predio)
    cidade.marcar_simulacao_suja()
    return True, f"Predio demolido. Reembolso de R$ {reembolso}.", reembolso


def melhorar(cidade, predio_id):
    if not sistema_desbloqueado("upgrades", cidade.dados["rodada"]):
        return False, "Melhorias de predios serao desbloqueadas na rodada 13."
    predio = encontrar_predio(cidade, predio_id)
    if not predio:
        return False, "Predio nao encontrado."
    atual = dados_construcao_nivel(predio["tipo"], predio["nivel"])
    custo = atual["custo_upgrade"]
    if custo is None:
        return False, "Este predio ja esta no nivel maximo."
    if cidade.dados["dinheiro"] < custo:
        falta = custo - cidade.dados["dinheiro"]
        return False, f"Dinheiro insuficiente para melhorar. Faltam R$ {falta}."
    cidade.dados["dinheiro"] -= custo
    predio["nivel"] += 1
    predio["investimento"] += custo
    cidade.marcar_simulacao_suja()
    nome = CONSTRUCOES[predio["tipo"]]["nome"]
    return True, f"{nome} melhorada para o nivel {predio['nivel']} por R$ {custo}."


def encontrar_predio(cidade, predio_id):
    return next((predio for predio in cidade.construcoes if predio["id"] == predio_id), None)


def validar_posicao(cidade, posicao):
    if not isinstance(posicao, int) or isinstance(posicao, bool):
        return "Posicao invalida no mapa."
    if posicao < 0 or posicao >= len(cidade.mapa):
        return "Nao e possivel construir fora do mapa."
    if cidade.mapa[posicao] is not None:
        return "Area ocupada."
    if not posicao_desbloqueada(cidade, posicao):
        return "Este terreno pertence a um setor bloqueado."
    if posicao in cidade.obstaculos:
        return "Remova o obstaculo antes de construir."
    if posicao in cidade.estradas:
        return "Esta area ja e ocupada por uma estrada."
    return None
