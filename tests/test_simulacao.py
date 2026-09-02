import unittest

from game import JogoCidade
from game.dados import MISSOES


class SimulacaoCidadeTest(unittest.TestCase):
    def setUp(self):
        self.jogo = JogoCidade()
        self.estado = self.jogo.novo_jogo("Ana")
        self.jogo.cidade.missoes_concluidas = {missao["id"] for missao in MISSOES}

    def test_estado_inicial_preserva_valores_e_detalha_economia(self):
        dados = self.estado["cidade"]["dados"]
        self.assertEqual((dados["energia"], dados["agua"], dados["qualidade_vida"]), (50, 75, 50))
        self.assertEqual(self.estado["economia"]["receitas"], 660)
        self.assertEqual(self.estado["economia"]["despesas"], 900)
        self.assertEqual(self.estado["economia"]["previsao"], -240)
        self.assertEqual(self.estado["economia"]["populacao_ativa"], 60)
        self.assertEqual(self.estado["economia"]["taxa_desemprego"], 50)

    def test_construcoes_sao_separadas_por_categoria(self):
        categorias = {item["id"] for item in self.estado["categorias_construcoes"]}
        self.assertIn("residencial", categorias)
        self.assertIn("saude", categorias)
        saude = next(item for item in self.estado["categorias_construcoes"] if item["id"] == "saude")
        self.assertFalse(saude["desbloqueada"])
        self.jogo.cidade.dados["rodada"] = 6
        estado_avancado = self.jogo.estado()
        categorias = {item["id"] for item in estado_avancado["categorias_construcoes"]}
        self.assertIn("saude", categorias)
        self.assertIn("infraestrutura", categorias)
        self.assertTrue(all(item["categoria"] in categorias for item in estado_avancado["construcoes_disponiveis"]))

    def test_construir_cobra_e_aplica_manutencao_uma_vez(self):
        self.jogo.cidade.dados["rodada"] = 6
        resposta = self.jogo.construir("hospital", 0)
        self.assertTrue(resposta["sucesso"])
        self.assertEqual(resposta["cidade"]["dados"]["dinheiro"], 7200)
        self.assertEqual(resposta["economia"]["manutencao"], 230)
        self.assertEqual(resposta["economia"]["previsao"], -470)
        repetida = self.jogo.construir("hospital", 0)
        self.assertFalse(repetida["sucesso"])
        self.assertEqual(repetida["cidade"]["dados"]["dinheiro"], 7200)
        self.assertEqual(len(repetida["cidade"]["construcoes"]), 1)
        rodada = self.jogo.proxima_rodada(6)
        self.assertEqual(rodada["resumo"]["dinheiro_final"], 7200 - 470)

    def test_falta_de_dinheiro_informa_valor(self):
        self.jogo.cidade.dados["rodada"] = 6
        self.jogo.cidade.dados["dinheiro"] = 100
        resposta = self.jogo.construir("hospital", 0)
        self.assertFalse(resposta["sucesso"])
        self.assertIn("Faltam R$ 2700", resposta["mensagem"])
        self.assertEqual(len(resposta["cidade"]["construcoes"]), 0)

    def test_mover_nao_cobra_nem_duplica_efeitos(self):
        self.jogo.cidade.dados["rodada"] = 6
        criada = self.jogo.construir("escola", 0)
        predio_id = criada["predio_id"]
        dinheiro = criada["cidade"]["dados"]["dinheiro"]
        resposta = self.jogo.mover(predio_id, 7)
        self.assertTrue(resposta["sucesso"])
        self.assertEqual(resposta["cidade"]["dados"]["dinheiro"], dinheiro)
        self.assertEqual(resposta["cidade"]["mapa"][7], predio_id)
        self.assertIsNone(resposta["cidade"]["mapa"][0])
        self.assertEqual(resposta["economia"]["manutencao"], 160)

    def test_demolir_remove_todos_os_efeitos(self):
        self.jogo.cidade.dados["rodada"] = 6
        criada = self.jogo.construir("hospital", 0)
        self.assertEqual(criada["cidade"]["dados"]["empregos"], 38)
        resposta = self.jogo.demolir(criada["predio_id"])
        self.assertTrue(resposta["sucesso"])
        self.assertEqual(resposta["cidade"]["dados"]["empregos"], 30)
        self.assertEqual(resposta["cidade"]["dados"]["saude"], 50)
        self.assertEqual(resposta["economia"]["manutencao"], 0)
        self.assertEqual(len(resposta["cidade"]["construcoes"]), 0)

    def test_upgrade_aumenta_beneficios_e_custos(self):
        self.jogo.cidade.dados["rodada"] = 13
        criada = self.jogo.construir("hospital", 0)
        resposta = self.jogo.melhorar(criada["predio_id"])
        predio = resposta["cidade"]["construcoes"][0]
        self.assertEqual(predio["nivel"], 2)
        self.assertGreater(predio["capacidade_saude"], 10)
        self.assertGreater(predio["manutencao"], 230)
        self.assertGreater(predio["consumo_energia"], 6)

    def test_sobrecarga_reduz_eficiencia(self):
        self.jogo.cidade.dados["rodada"] = 13
        self.jogo.cidade.dados["dinheiro"] = 100000
        for posicao in range(5):
            self.jogo.construir("fabrica", posicao)
        resposta = self.jogo.construir("hospital", 5)
        hospital = next(item for item in resposta["cidade"]["construcoes"] if item["tipo"] == "hospital")
        self.assertGreater(resposta["cidade"]["simulacao"]["energia"]["sobrecarga"], 0)
        self.assertLess(hospital["eficiencia"], 100)
        self.assertLess(hospital["capacidade_saude"] * hospital["eficiencia"] / 100, hospital["capacidade_saude"])

    def test_imposto_altera_previsao_e_qualidade_gradualmente(self):
        self.jogo.cidade.dados["rodada"] = 9
        anterior = self.estado["economia"]["previsao"]
        resposta = self.jogo.alterar_imposto("residencial", 1)
        self.assertGreater(resposta["economia"]["previsao"], anterior)
        self.assertLessEqual(resposta["cidade"]["dados"]["qualidade_vida"], 50)

    def test_fabrica_reduz_desemprego_e_parque_reduz_poluicao(self):
        self.jogo.cidade.dados["rodada"] = 9
        fabrica = self.jogo.construir("fabrica", 0)
        self.assertLess(fabrica["economia"]["taxa_desemprego"], 50)
        parque = self.jogo.construir("parque", 1)
        self.assertLess(parque["cidade"]["dados"]["poluicao"], fabrica["cidade"]["dados"]["poluicao"])


if __name__ == "__main__":
    unittest.main()
