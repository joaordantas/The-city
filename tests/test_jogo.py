import unittest
from concurrent.futures import ThreadPoolExecutor

from game import JogoCidade


class JogoCidadeTest(unittest.TestCase):
    def setUp(self):
        self.jogo = JogoCidade()
        self.jogo.novo_jogo("Ana")

    def test_configuracao_progressiva_das_rodadas(self):
        faixas = self.jogo.estado()["config_rodadas"]["duracoes"]
        self.assertEqual([faixa["tempo"] for faixa in faixas], [60, 60, 55, 50, 45])

    def test_mesma_rodada_nao_e_processada_duas_vezes(self):
        primeira = self.jogo.proxima_rodada(rodada_esperada=1)
        repetida = self.jogo.proxima_rodada(rodada_esperada=1)

        self.assertTrue(primeira["sucesso"])
        self.assertFalse(repetida["sucesso"])
        self.assertTrue(repetida["rodada_ja_processada"])
        self.assertEqual(repetida["cidade"]["dados"]["rodada"], 2)

    def test_chamadas_simultaneas_processam_uma_unica_vez(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            respostas = list(executor.map(lambda _: self.jogo.proxima_rodada(1), range(2)))

        self.assertEqual(sum(resposta["sucesso"] for resposta in respostas), 1)
        self.assertEqual(self.jogo.cidade.dados["rodada"], 2)

    def test_resumo_informa_variacoes_da_rodada(self):
        resposta = self.jogo.proxima_rodada(rodada_esperada=1)
        self.assertEqual(
            set(resposta["resumo"]["variacoes"]),
            {"dinheiro", "populacao", "empregos", "qualidade_vida"},
        )

    def test_rodada_final_nao_avanca_para_21(self):
        self.jogo.cidade.dados["rodada"] = 20
        resposta = self.jogo.proxima_rodada(rodada_esperada=20)

        self.assertEqual(resposta["cidade"]["status"], "concluido")
        self.assertEqual(resposta["cidade"]["dados"]["rodada"], 20)


if __name__ == "__main__":
    unittest.main()
