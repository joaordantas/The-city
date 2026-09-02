from threading import Lock

from .avaliacao import calcular_avaliacao
from .cidade import Cidade
from .construcoes import (
    construir,
    demolir,
    listar_categorias,
    listar_construcoes,
    melhorar,
    mover,
)
from .crises import atualizar_crises, resumo_crises
from .dados import CONFIG_IMPOSTOS, CONFIG_RODADAS, CONFIG_SIMULACAO
from .economia import calcular_economia, processar_rodada
from .eventos import (
    avancar_modificadores,
    processar_consequencias_futuras,
    responder_evento,
    resolver_evento_ignorado,
    sortear_evento,
)
from .missoes import avaliar_missoes, resumo_missoes
from .logistica import atualizar_pedido, entregar_pedido, recusar_pedido, resumo_logistica
from .producao import resumo_producao
from .projetos import investir_projeto, listar_projetos
from .progressao import (
    avaliar_plano_governo,
    listar_desbloqueios,
    obter_progressao,
    sistema_desbloqueado,
)
from .territorio import construir_estrada, desbloquear_setor, remover_obstaculo, resumo_territorio


TUTORIAL = {
    "obrigatorio": True,
    "etapas": [
        {
            "titulo": "Voce tem 60 segundos",
            "texto": "Na primeira rodada, observe dinheiro, populacao, qualidade, energia e agua antes de construir.",
        },
        {
            "titulo": "Missoes orientam o inicio",
            "texto": "Acompanhe no maximo tres missoes. Cada recompensa e paga apenas uma vez.",
        },
        {
            "titulo": "A cidade reage",
            "texto": "O tempo continua durante eventos. Se uma decisao for ignorada, a consequencia aparece no fim da rodada.",
        },
    ],
}


def _conselheiro(cidade):
    if cidade.status != "jogando" and cidade.avaliacao_final:
        return {
            "id": "encerramento",
            "nome": "Chefe de gabinete",
            "mensagem": f"O mandato terminou como {cidade.avaliacao_final['classificacao']}. O relatorio mostra onde a cidade avancou e onde ficou vulneravel.",
            "prioridade": "final",
        }
    if cidade.crises_ativas:
        crise = cidade.crises_ativas[0]
        return {
            "id": f"crise-{crise['id']}-{crise['rodadas']}",
            "nome": "Chefe de gabinete",
            "mensagem": f"{crise['titulo']}: restam {crise['restantes']} rodadas para recuperar a cidade.",
            "prioridade": "critica",
        }
    mensagens = {
        3: ("Secretaria de Obras", "Agua, energia, empregos e eventos foram liberados. Cresca sem sobrecarregar as redes."),
        6: ("Secretaria Social", "Saude e educacao agora entram no centro das decisoes."),
        9: ("Secretaria da Fazenda", "Impostos e industria foram liberados. Receita maior tambem pode reduzir o bem-estar."),
        13: ("Planejamento Urbano", "Melhorias de predios foram liberadas; crises combinadas passam a ser mais provaveis."),
        17: ("Chefe de gabinete", "Reta final: o relatorio considera medias da gestao, nao apenas o caixa."),
    }
    if cidade.dados["rodada"] in mensagens:
        nome, mensagem = mensagens[cidade.dados["rodada"]]
        return {"id": f"rodada-{cidade.dados['rodada']}", "nome": nome, "mensagem": mensagem, "prioridade": "normal"}
    return None


class JogoCidade:
    def __init__(self):
        self.cidade = Cidade()
        self._bloqueio = Lock()

    def novo_jogo(self, prefeito):
        with self._bloqueio:
            self.cidade = Cidade(prefeito)
            self.cidade.registrar_historico(
                "inicio",
                "Bem-vindo a Cidade em Equilibrio",
                "A gestao comecou com 20 rodadas pela frente.",
            )
            return self.estado()

    def estado(self):
        rodada = self.cidade.dados["rodada"]
        cidade = self.cidade.to_dict()
        return {
            "cidade": cidade,
            "construcoes_disponiveis": listar_construcoes(rodada),
            "categorias_construcoes": listar_categorias(rodada),
            "economia": calcular_economia(self.cidade),
            "missoes": resumo_missoes(self.cidade),
            "progressao": obter_progressao(rodada),
            "crises": resumo_crises(self.cidade),
            "territorio": resumo_territorio(self.cidade),
            "producao": resumo_producao(self.cidade),
            "logistica": resumo_logistica(self.cidade),
            "projetos": listar_projetos(self.cidade),
            "plano_governo": avaliar_plano_governo(self.cidade),
            "conselheiro": _conselheiro(self.cidade),
            "tutorial": TUTORIAL,
            "config_rodadas": CONFIG_RODADAS,
            "config_impostos": {
                "minimo": CONFIG_IMPOSTOS["minimo"],
                "maximo": CONFIG_IMPOSTOS["maximo"],
                "passo": CONFIG_IMPOSTOS["passo"],
            },
            "config_construcoes": {"reembolso_demolicao": CONFIG_SIMULACAO["reembolso_demolicao"]},
        }

    def _partida_ativa(self):
        return self.cidade.status == "jogando"

    def _resposta_acao(self, sucesso, mensagem, **extras):
        concluidas = avaliar_missoes(self.cidade) if sucesso else []
        if concluidas:
            mensagem += " Missao concluida: " + ", ".join(item["titulo"] for item in concluidas) + "."
        return {"sucesso": sucesso, "mensagem": mensagem, **extras, **self.estado()}

    def construir(self, tipo, posicao):
        with self._bloqueio:
            if not self._partida_ativa():
                return self._resposta_acao(False, "A partida ja terminou.")
            sucesso, mensagem, predio_id = construir(self.cidade, tipo, posicao)
            if sucesso:
                self.cidade.registrar_historico("construcao", "Nova construcao", mensagem)
            return self._resposta_acao(sucesso, mensagem, predio_id=predio_id)

    def mover(self, predio_id, posicao):
        with self._bloqueio:
            if not self._partida_ativa():
                return self._resposta_acao(False, "A partida ja terminou.")
            sucesso, mensagem = mover(self.cidade, predio_id, posicao)
            if sucesso:
                self.cidade.registrar_historico("construcao", "Predio movido", mensagem)
            return self._resposta_acao(sucesso, mensagem)

    def demolir(self, predio_id):
        with self._bloqueio:
            if not self._partida_ativa():
                return self._resposta_acao(False, "A partida ja terminou.", reembolso=0)
            sucesso, mensagem, reembolso = demolir(self.cidade, predio_id)
            if sucesso:
                self.cidade.registrar_historico("construcao", "Demolicao", mensagem)
            return self._resposta_acao(sucesso, mensagem, reembolso=reembolso)

    def melhorar(self, predio_id):
        with self._bloqueio:
            if not self._partida_ativa():
                return self._resposta_acao(False, "A partida ja terminou.")
            sucesso, mensagem = melhorar(self.cidade, predio_id)
            if sucesso:
                self.cidade.registrar_historico("construcao", "Predio melhorado", mensagem)
            return self._resposta_acao(sucesso, mensagem)

    def expandir(self, setor_id):
        with self._bloqueio:
            if not self._partida_ativa():
                return self._resposta_acao(False, "A partida ja terminou.")
            sucesso, mensagem = desbloquear_setor(self.cidade, setor_id)
            return self._resposta_acao(sucesso, mensagem)

    def remover_obstaculo(self, posicao):
        with self._bloqueio:
            if not self._partida_ativa():
                return self._resposta_acao(False, "A partida ja terminou.")
            sucesso, mensagem = remover_obstaculo(self.cidade, posicao)
            if sucesso:
                self.cidade.registrar_historico("expansao", "Terreno liberado", mensagem)
            return self._resposta_acao(sucesso, mensagem)

    def construir_estrada(self, posicao):
        with self._bloqueio:
            if not self._partida_ativa():
                return self._resposta_acao(False, "A partida ja terminou.")
            sucesso, mensagem = construir_estrada(self.cidade, posicao)
            if sucesso:
                self.cidade.registrar_historico("infraestrutura", "Nova estrada", mensagem)
            return self._resposta_acao(sucesso, mensagem)

    def entregar_pedido(self):
        with self._bloqueio:
            if not self._partida_ativa():
                return self._resposta_acao(False, "A partida ja terminou.")
            sucesso, mensagem = entregar_pedido(self.cidade)
            return self._resposta_acao(sucesso, mensagem)

    def recusar_pedido(self):
        with self._bloqueio:
            if not self._partida_ativa():
                return self._resposta_acao(False, "A partida ja terminou.")
            sucesso, mensagem = recusar_pedido(self.cidade)
            return self._resposta_acao(sucesso, mensagem)

    def investir_projeto(self, projeto_id):
        with self._bloqueio:
            if not self._partida_ativa():
                return self._resposta_acao(False, "A partida ja terminou.")
            sucesso, mensagem, concluido = investir_projeto(self.cidade, projeto_id)
            return self._resposta_acao(sucesso, mensagem, projeto_concluido=concluido)

    def alterar_imposto(self, tipo, direcao):
        with self._bloqueio:
            if not self._partida_ativa():
                return self._resposta_acao(False, "A partida ja terminou.")
            if not sistema_desbloqueado("impostos", self.cidade.dados["rodada"]):
                return self._resposta_acao(False, "Impostos serao desbloqueados na rodada 9.")
            if tipo not in self.cidade.impostos or direcao not in (-1, 1):
                return self._resposta_acao(False, "Alteracao de imposto invalida.")
            atual = self.cidade.impostos[tipo]
            novo = max(
                CONFIG_IMPOSTOS["minimo"],
                min(CONFIG_IMPOSTOS["maximo"], atual + direcao * CONFIG_IMPOSTOS["passo"]),
            )
            if novo == atual:
                return self._resposta_acao(False, "Este imposto ja esta no limite.")
            self.cidade.impostos[tipo] = novo
            self.cidade.marcar_simulacao_suja()
            mensagem = f"Imposto alterado para {novo}%."
            self.cidade.registrar_historico("imposto", "Taxa alterada", mensagem)
            return self._resposta_acao(True, mensagem)

    def responder_evento(self, escolha_id):
        with self._bloqueio:
            if not self._partida_ativa():
                return self._resposta_acao(False, "A partida ja terminou.")
            sucesso, mensagem, efeitos = responder_evento(self.cidade, escolha_id)
            return self._resposta_acao(sucesso, mensagem, efeitos=efeitos)

    def proxima_rodada(self, rodada_esperada=None):
        with self._bloqueio:
            rodada_atual = self.cidade.dados["rodada"]
            if rodada_esperada is not None and rodada_esperada != rodada_atual:
                return {
                    "sucesso": False,
                    "rodada_ja_processada": True,
                    "mensagem": "Esta rodada ja foi processada.",
                    **self.estado(),
                }
            if not self._partida_ativa():
                return {"sucesso": False, "mensagem": "A partida ja terminou.", **self.estado()}

            antes = self.cidade.dados.copy()
            futuras = processar_consequencias_futuras(self.cidade)
            ignorado = resolver_evento_ignorado(self.cidade)
            resumo = processar_rodada(self.cidade)
            crise = atualizar_crises(self.cidade)
            self.cidade.registrar_metricas(rodada_atual, resumo["resultado"])
            missoes = avaliar_missoes(self.cidade)
            expirados = avancar_modificadores(self.cidade)

            proxima = rodada_atual
            desbloqueios = []
            if self.cidade.status == "jogando":
                if rodada_atual >= self.cidade.dados["max_rodadas"]:
                    self.cidade.status = "concluido"
                    self.cidade.motivo_fim = "Mandato de 20 rodadas concluido"
                else:
                    proxima = rodada_atual + 1
                    desbloqueios = listar_desbloqueios(rodada_atual, proxima)
                    self.cidade.dados["rodada"] = proxima

            if self.cidade.status == "jogando":
                atualizar_pedido(self.cidade)

            evento = None
            if self.cidade.status == "jogando":
                evento = sortear_evento(self.cidade)
            else:
                self.cidade.marcar_simulacao_suja()
                self.cidade.avaliacao_final = calcular_avaliacao(self.cidade)

            self.cidade.marcar_simulacao_suja()
            self.cidade.recalcular_simulacao()
            depois = self.cidade.dados
            resumo.update({
                "variacoes": {
                    chave: depois[chave] - antes[chave]
                    for chave in ("dinheiro", "populacao", "empregos", "qualidade_vida")
                },
                "evento_ignorado": ignorado,
                "consequencias_futuras": futuras,
                "modificadores_expirados": expirados,
                "missoes_concluidas": [item["titulo"] for item in missoes],
                "desbloqueios": desbloqueios,
                "crise": crise,
            })
            mensagem = f"Rodada {rodada_atual} processada. Resultado: R$ {resumo['resultado']}."
            if ignorado:
                mensagem += f" O evento {ignorado['titulo']} foi ignorado."
            if evento:
                mensagem += f" Nova decisao: {evento['titulo']}."
            if desbloqueios:
                mensagem += " Desbloqueado: " + ", ".join(item["titulo"] for item in desbloqueios) + "."
            self.cidade.registrar_historico("rodada", f"Rodada {rodada_atual}", mensagem, rodada=rodada_atual)
            return {"sucesso": True, "mensagem": mensagem, "resumo": resumo, **self.estado()}

    def reiniciar(self):
        with self._bloqueio:
            prefeito = self.cidade.prefeito
            self.cidade = Cidade(prefeito)
            self.cidade.registrar_historico(
                "inicio",
                "Cidade reiniciada",
                "O estado anterior, temporizadores e progresso foram descartados.",
            )
            return {"sucesso": True, "mensagem": "Cidade reiniciada.", **self.estado()}
