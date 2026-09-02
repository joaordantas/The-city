from copy import deepcopy

from .dados import PROJETOS_ESPECIAIS


def listar_projetos(cidade):
    resultado = []
    for projeto_id, projeto in PROJETOS_ESPECIAIS.items():
        etapa = cidade.projetos_em_andamento.get(projeto_id, 0)
        concluido = projeto_id in cidade.projetos_concluidos
        resultado.append({
            "id": projeto_id,
            **deepcopy(projeto),
            "etapa_atual": etapa,
            "total_etapas": len(projeto["etapas"]),
            "concluido": concluido,
            "disponivel": cidade.dados["rodada"] >= projeto["rodada_desbloqueio"],
            "proxima_etapa": None if concluido else deepcopy(projeto["etapas"][etapa]),
        })
    return resultado


def investir_projeto(cidade, projeto_id):
    projeto = PROJETOS_ESPECIAIS.get(projeto_id)
    if not projeto:
        return False, "Projeto especial desconhecido.", False
    if cidade.dados["rodada"] < projeto["rodada_desbloqueio"]:
        return False, f"Este projeto sera liberado na rodada {projeto['rodada_desbloqueio']}.", False
    if projeto_id in cidade.projetos_concluidos:
        return False, "Este projeto ja foi concluido.", False
    etapa = cidade.projetos_em_andamento.get(projeto_id, 0)
    custo = projeto["etapas"][etapa]
    if cidade.dados["dinheiro"] < custo["dinheiro"]:
        return False, f"Dinheiro insuficiente. Faltam R$ {custo['dinheiro'] - cidade.dados['dinheiro']}.", False
    if cidade.estoque["materiais"] < custo["materiais"]:
        return False, f"Materiais insuficientes. Faltam {custo['materiais'] - cidade.estoque['materiais']}.", False
    cidade.dados["dinheiro"] -= custo["dinheiro"]
    cidade.estoque["materiais"] -= custo["materiais"]
    etapa += 1
    concluido = etapa >= len(projeto["etapas"])
    if concluido:
        cidade.projetos_concluidos.add(projeto_id)
        cidade.projetos_em_andamento.pop(projeto_id, None)
        cidade.registrar_historico("projeto", f"Projeto concluido: {projeto['nome']}", "O beneficio estrutural foi ativado permanentemente.")
    else:
        cidade.projetos_em_andamento[projeto_id] = etapa
        cidade.registrar_historico("projeto", f"Etapa {etapa} de {projeto['nome']}", "O investimento foi registrado sem antecipar o beneficio final.")
    cidade.marcar_simulacao_suja()
    mensagem = f"{projeto['nome']}: etapa {etapa}/{len(projeto['etapas'])} concluida."
    if concluido:
        mensagem += " Projeto concluido e beneficios ativados."
    return True, mensagem, concluido


def efeitos_projetos(cidade):
    efeitos = {}
    for projeto_id in cidade.projetos_concluidos:
        for chave, valor in PROJETOS_ESPECIAIS[projeto_id]["efeitos"].items():
            efeitos[chave] = efeitos.get(chave, 0) + valor
    return efeitos
