import unittest
from unittest.mock import patch

from game import JogoCidade
from game.avaliacao import calcular_avaliacao
from game.cidade import Cidade
from game.crises import atualizar_crises
from game.dados import MISSOES
from game.eventos import (
    avancar_modificadores,
    iniciar_evento,
    processar_consequencias_futuras,
    resolver_evento_ignorado,
)


class Parte3Test(unittest.TestCase):
    def setUp(self):
        self.jogo = JogoCidade()
        self.jogo.novo_jogo("Ana")

    def test_missao_paga_recompensa_uma_unica_vez(self):
        primeira = self.jogo.construir("casa", 0)
        self.assertEqual(primeira["cidade"]["dados"]["dinheiro"], 10000 - 900 + 500)
        self.assertIn("primeira_moradia", primeira["missoes"]["concluidas"])

        dinheiro = primeira["cidade"]["dados"]["dinheiro"]
        segunda_avaliacao = self.jogo.mover(primeira["predio_id"], 1)
        self.assertEqual(segunda_avaliacao["cidade"]["dados"]["dinheiro"], dinheiro)
        self.assertEqual(segunda_avaliacao["missoes"]["concluidas"].count("primeira_moradia"), 1)

    def test_escolha_de_evento_aplica_custo_e_modificador(self):
        self.jogo.cidade.dados["rodada"] = 6
        self.jogo.cidade.missoes_concluidas = {missao["id"] for missao in MISSOES}
        iniciar_evento(self.jogo.cidade, "epidemia")
        dinheiro = self.jogo.cidade.dados["dinheiro"]
        resposta = self.jogo.responder_evento("campanha")

        self.assertTrue(resposta["sucesso"])
        self.assertEqual(resposta["cidade"]["dados"]["dinheiro"], dinheiro - 500)
        self.assertIsNone(resposta["cidade"]["evento_ativo"])
        self.assertEqual(resposta["cidade"]["modificadores"][0]["rodadas_restantes"], 2)

    @patch("game.jogo.sortear_evento", return_value=None)
    def test_evento_ignorado_aplica_consequencia_no_fim(self, _sortear):
        self.jogo.cidade.dados["rodada"] = 3
        iniciar_evento(self.jogo.cidade, "seca")
        resposta = self.jogo.proxima_rodada(3)

        self.assertEqual(resposta["resumo"]["evento_ignorado"]["id"], "seca")
        self.assertIsNone(resposta["cidade"]["evento_ativo"])
        self.assertTrue(any(item["nome"] == "Reservatorios vazios" for item in resposta["cidade"]["modificadores"]))

    def test_modificador_expira_por_rodadas_sem_timer_proprio(self):
        self.jogo.cidade.dados["rodada"] = 3
        iniciar_evento(self.jogo.cidade, "seca")
        self.jogo.responder_evento("racionar")

        self.assertEqual({item["rodadas_restantes"] for item in self.jogo.cidade.modificadores}, {2})
        avancar_modificadores(self.jogo.cidade)
        self.assertEqual({item["rodadas_restantes"] for item in self.jogo.cidade.modificadores}, {1})
        expirados = avancar_modificadores(self.jogo.cidade)
        self.assertEqual(len(expirados), 2)
        self.assertEqual(self.jogo.cidade.modificadores, [])

    def test_consequencia_futura_acontece_na_rodada_prevista(self):
        self.jogo.cidade.dados["rodada"] = 6
        iniciar_evento(self.jogo.cidade, "epidemia")
        resolver_evento_ignorado(self.jogo.cidade)
        dinheiro = self.jogo.cidade.dados["dinheiro"]

        self.assertEqual(processar_consequencias_futuras(self.jogo.cidade), [])
        aplicadas = processar_consequencias_futuras(self.jogo.cidade)
        self.assertEqual(aplicadas[0]["titulo"], "Conta hospitalar atrasada")
        self.assertEqual(self.jogo.cidade.dados["dinheiro"], dinheiro - 800)

    def test_crise_pode_ser_superada_e_tambem_causar_derrota(self):
        cidade = Cidade("Ana")
        cidade.dados["dinheiro"] = -1
        atualizar_crises(cidade)
        cidade.dados["dinheiro"] = 1000
        recuperacao = atualizar_crises(cidade)
        self.assertEqual(recuperacao["recuperadas"][0]["id"], "financeira")
        self.assertEqual(cidade.status, "jogando")

        cidade.dados["dinheiro"] = -1
        for _ in range(3):
            atualizar_crises(cidade)
        self.assertEqual(cidade.status, "derrota")
        self.assertEqual(cidade.motivo_fim, "Crise financeira")

    @patch("game.jogo.sortear_evento", return_value=None)
    def test_rodada_20_encerra_sem_criar_21_e_calcula_pontuacao(self, _sortear):
        self.jogo.cidade.dados["rodada"] = 20
        resposta = self.jogo.proxima_rodada(20)

        self.assertEqual(resposta["cidade"]["status"], "concluido")
        self.assertEqual(resposta["cidade"]["dados"]["rodada"], 20)
        self.assertGreaterEqual(resposta["cidade"]["avaliacao_final"]["total"], 0)
        self.assertLessEqual(resposta["cidade"]["avaliacao_final"]["total"], 7000)

    def test_cidade_equilibrada_supera_cidade_com_apenas_caixa(self):
        caixa = Cidade("Caixa")
        caixa.dados["dinheiro"] = 30000
        caixa.historico_metricas = [{"resultado": 2000, "saude": 20, "educacao": 20, "taxa_desemprego": 70, "poluicao": 90, "qualidade_vida": 20}]
        equilibrada = Cidade("Equilibrada")
        equilibrada.dados.update({"dinheiro": 12000, "saude": 85, "educacao": 85, "poluicao": 10, "qualidade_vida": 82})
        equilibrada.historico_metricas = [{"resultado": 500, "saude": 85, "educacao": 85, "taxa_desemprego": 10, "poluicao": 10, "qualidade_vida": 82}]

        self.assertGreater(calcular_avaliacao(equilibrada)["total"], calcular_avaliacao(caixa)["total"])

    def test_progressao_aumenta_dificuldade_e_nao_libera_tudo_no_inicio(self):
        inicial = self.jogo.estado()
        desbloqueadas = {item["id"] for item in inicial["construcoes_disponiveis"] if item["desbloqueada"]}
        self.assertEqual(desbloqueadas, {"casa", "parque"})
        self.assertIn("saude", {item["id"] for item in inicial["categorias_construcoes"]})
        self.assertFalse(inicial["progressao"]["sistemas"]["impostos"]["desbloqueado"])

        self.jogo.cidade.dados["rodada"] = 13
        avancado = self.jogo.estado()
        self.assertGreaterEqual(sum(item["desbloqueada"] for item in avancado["construcoes_disponiveis"]), 8)
        self.assertTrue(avancado["progressao"]["sistemas"]["impostos"]["desbloqueado"])
        self.assertTrue(avancado["progressao"]["sistemas"]["upgrades"]["desbloqueado"])
        self.assertGreater(avancado["progressao"]["fase"]["intensidade_eventos"], inicial["progressao"]["fase"]["intensidade_eventos"])


if __name__ == "__main__":
    unittest.main()
