import time
import unittest
from unittest.mock import patch

from game import JogoCidade
from game.dados import MISSOES
from game.logistica import atualizar_pedido
from game.producao import processar_producao


class Parte4Test(unittest.TestCase):
    def setUp(self):
        self.jogo = JogoCidade()
        self.jogo.novo_jogo("Ana")

    def avancar_para(self, rodada):
        self.jogo.cidade.dados["rodada"] = rodada
        self.jogo.cidade.dados["dinheiro"] = 100_000
        self.jogo.cidade.missoes_concluidas = {missao["id"] for missao in MISSOES}
        self.jogo.cidade.marcar_simulacao_suja()

    def test_expansao_cobra_uma_vez_e_libera_construcao(self):
        self.avancar_para(6)
        bloqueada = self.jogo.construir("fazenda", 16)
        self.assertFalse(bloqueada["sucesso"])

        dinheiro = self.jogo.cidade.dados["dinheiro"]
        expansao = self.jogo.expandir("norte")
        self.assertTrue(expansao["sucesso"])
        self.assertEqual(expansao["cidade"]["dados"]["dinheiro"], dinheiro - 2800)
        self.assertFalse(self.jogo.expandir("norte")["sucesso"])
        self.assertTrue(self.jogo.construir("fazenda", 16)["sucesso"])

    def test_obstaculo_precisa_ser_removido_e_tem_custo(self):
        self.avancar_para(6)
        self.jogo.expandir("norte")
        self.assertFalse(self.jogo.construir("fazenda", 18)["sucesso"])
        dinheiro = self.jogo.cidade.dados["dinheiro"]
        resposta = self.jogo.remover_obstaculo(18)
        self.assertTrue(resposta["sucesso"])
        self.assertEqual(resposta["cidade"]["dados"]["dinheiro"], dinheiro - 250)
        self.assertTrue(self.jogo.construir("fazenda", 18)["sucesso"])

    def test_estrada_recupera_eficiencia_de_predio_isolado(self):
        self.avancar_para(9)
        predio = self.jogo.construir("fabrica", 7)
        self.assertEqual(next(item for item in predio["cidade"]["construcoes"] if item["id"] == predio["predio_id"])["eficiencia"], 70)
        estrada = self.jogo.construir_estrada(6)
        detalhe = next(item for item in estrada["cidade"]["construcoes"] if item["id"] == predio["predio_id"])
        self.assertTrue(estrada["sucesso"])
        self.assertEqual(detalhe["eficiencia"], 100)

    def test_producao_usa_eficiencia_e_nao_exige_coleta(self):
        self.avancar_para(9)
        self.jogo.construir_estrada(6)
        self.jogo.construir("fabrica", 7)
        self.jogo.cidade.modificadores.append({"alvo": "eficiencia_industria_pct", "valor": -20})
        self.jogo.cidade.marcar_simulacao_suja()
        resumo = processar_producao(self.jogo.cidade)
        self.assertEqual(resumo["produzido"]["materiais"], 16)
        self.assertEqual(resumo["produzido"]["mercadorias"], 18)
        self.assertEqual(self.jogo.cidade.estoque["materiais"], 16)

    def test_estoque_respeita_limite_e_armazem_aumenta_capacidade(self):
        self.avancar_para(9)
        self.jogo.construir("armazem", 0)
        self.jogo.construir("fabrica", 1)
        self.assertEqual(self.jogo.estado()["producao"]["capacidade"], 300)
        self.jogo.cidade.estoque["materiais"] = 295
        resumo = processar_producao(self.jogo.cidade)
        self.assertEqual(self.jogo.cidade.estoque["materiais"], 300)
        self.assertGreater(resumo["descartado"]["materiais"], 0)

    def test_pedido_logistico_e_atomico_e_nao_duplica_recompensa(self):
        self.avancar_para(9)
        pedido = atualizar_pedido(self.jogo.cidade)
        dinheiro = self.jogo.cidade.dados["dinheiro"]
        self.assertFalse(self.jogo.entregar_pedido()["sucesso"])
        self.assertEqual(self.jogo.cidade.dados["dinheiro"], dinheiro)
        self.jogo.cidade.estoque.update(pedido["recursos"])
        entregue = self.jogo.entregar_pedido()
        self.assertTrue(entregue["sucesso"])
        self.assertEqual(entregue["cidade"]["dados"]["dinheiro"], dinheiro + pedido["recompensa"])
        self.assertFalse(self.jogo.entregar_pedido()["sucesso"])

    def test_projeto_so_aplica_beneficio_apos_ultima_etapa(self):
        self.avancar_para(13)
        self.jogo.cidade.estoque["materiais"] = 500
        energia_base = self.jogo.estado()["cidade"]["simulacao"]["energia"]["capacidade"]
        for _ in range(2):
            resposta = self.jogo.investir_projeto("usina_municipal")
            self.assertTrue(resposta["sucesso"])
            self.assertFalse(resposta["projeto_concluido"])
            self.assertEqual(resposta["cidade"]["simulacao"]["energia"]["capacidade"], energia_base)
        final = self.jogo.investir_projeto("usina_municipal")
        self.assertTrue(final["projeto_concluido"])
        self.assertEqual(final["cidade"]["simulacao"]["energia"]["capacidade"], energia_base + 60)

    def test_limite_de_construcao_especial(self):
        self.avancar_para(9)
        self.assertTrue(self.jogo.construir("centro_distribuicao", 0)["sucesso"])
        self.assertFalse(self.jogo.construir("centro_distribuicao", 1)["sucesso"])

    def test_reinicio_limpa_todo_estado_avancado(self):
        self.avancar_para(13)
        self.jogo.expandir("norte")
        self.jogo.construir_estrada(0)
        self.jogo.cidade.estoque["materiais"] = 100
        self.jogo.investir_projeto("parque_central")
        resposta = self.jogo.reiniciar()
        self.assertEqual(resposta["cidade"]["dados"]["rodada"], 1)
        self.assertEqual(resposta["cidade"]["estradas"], [])
        self.assertEqual(resposta["cidade"]["estoque"], {"alimentos": 0, "materiais": 0, "mercadorias": 0})
        self.assertEqual(resposta["cidade"]["projetos_em_andamento"], {})
        self.assertEqual(resposta["cidade"]["setores_desbloqueados"], ["centro"])

    @patch("game.jogo.sortear_evento", return_value=None)
    def test_partida_completa_chega_a_rodada_20_sem_estado_duplicado(self, _sortear):
        self.jogo.cidade.dados["dinheiro"] = 100_000
        for rodada in range(1, 21):
            resposta = self.jogo.proxima_rodada(rodada)
            if rodada < 20:
                self.assertEqual(resposta["cidade"]["dados"]["rodada"], rodada + 1)
        self.assertEqual(resposta["cidade"]["status"], "concluido")
        self.assertEqual(len(self.jogo.cidade.historico_metricas), 20)

    def test_estado_de_cidade_grande_permanece_rapido(self):
        self.avancar_para(13)
        self.jogo.cidade.setores_desbloqueados.update({"norte", "industrial", "rural"})
        self.jogo.cidade.obstaculos.clear()
        tipos = ["casa", "comercio", "fabrica", "escola", "hospital", "fazenda", "armazem", "parque"]
        for posicao in range(30):
            self.jogo.construir(tipos[posicao % len(tipos)], posicao)
        inicio = time.perf_counter()
        for _ in range(100):
            estado = self.jogo.estado()
        self.assertEqual(len(estado["territorio"]["celulas"]), 36)
        self.assertLess(time.perf_counter() - inicio, 1.0)


if __name__ == "__main__":
    unittest.main()
