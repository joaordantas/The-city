import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from game import JogoCidade
from game.persistencia import RepositorioPartidas


class PersistenciaETimerTest(unittest.TestCase):
    def test_partidas_sao_isoladas_e_retomadas_do_disco(self):
        with tempfile.TemporaryDirectory() as pasta:
            repositorio = RepositorioPartidas(Path(pasta) / "partidas.sqlite3")
            jogo_a = JogoCidade()
            jogo_b = JogoCidade()
            jogo_a.novo_jogo("Ana")
            jogo_b.novo_jogo("Bia")
            jogo_a.construir("casa", 0)
            repositorio.salvar("a", jogo_a)
            repositorio.salvar("b", jogo_b)

            carregado_a = repositorio.carregar("a")
            carregado_b = repositorio.carregar("b")
            self.assertEqual(carregado_a.cidade.prefeito, "Ana")
            self.assertEqual(len(carregado_a.cidade.construcoes), 1)
            self.assertEqual(carregado_b.cidade.prefeito, "Bia")
            self.assertEqual(carregado_b.cidade.construcoes, [])

    def test_cronometro_persiste_e_desconta_tempo_real(self):
        with tempfile.TemporaryDirectory() as pasta:
            repositorio = RepositorioPartidas(Path(pasta) / "partidas.sqlite3")
            jogo = JogoCidade()
            jogo.novo_jogo("Ana")
            with patch("game.jogo.time", return_value=100):
                jogo.retomar_timer()
                repositorio.salvar("timer", jogo)

            carregado = repositorio.carregar("timer")
            with patch("game.jogo.time", return_value=110):
                self.assertEqual(carregado.estado()["timer"]["restante_ms"], 50_000)
                pausado = carregado.pausar_timer()
            self.assertTrue(pausado["timer"]["pausado"])
            self.assertEqual(pausado["timer"]["restante_ms"], 50_000)


class BalanceamentoTest(unittest.TestCase):
    PLANO_CONSTRUCOES = {
        1: [("casa", 0), ("parque", 1)],
        3: [("comercio", 2), ("comercio", 3), ("estacao_agua", 4), ("usina_solar", 5)],
        6: [("escola", 6), ("hospital", 11)],
        9: [("fabrica", 12)],
        10: [("fazenda", 13)],
        12: [("escola", 14)],
    }

    def _jogar_partida(self, semente):
        random.seed(semente)
        jogo = JogoCidade()
        jogo.novo_jogo(f"Teste {semente}")
        for rodada in range(1, 21):
            if jogo.cidade.evento_ativo:
                escolhas = jogo.cidade.evento_ativo["escolhas"]
                escolha = min(
                    escolhas,
                    key=lambda item: sum(
                        -efeito.get("valor", 0)
                        for efeito in item["efeitos"]
                        if efeito["tipo"] == "dinheiro"
                    ),
                )
                jogo.responder_evento(escolha["id"])

            for tipo, posicao in self.PLANO_CONSTRUCOES.get(rodada, []):
                jogo.construir(tipo, posicao)
            if rodada == 9:
                for tipo, aumentos in (("residencial", 2), ("comercio", 1), ("industria", 2)):
                    for _ in range(aumentos):
                        jogo.alterar_imposto(tipo, 1)
            if rodada == 12:
                jogo.entregar_pedido()
            if rodada == 14:
                jogo.entregar_pedido()
                jogo.investir_projeto("parque_central")
            if rodada == 15:
                jogo.investir_projeto("parque_central")
            if rodada == 17:
                jogo.investir_projeto("parque_central")

            resposta = jogo.proxima_rodada(rodada)
            if resposta["cidade"]["status"] != "jogando":
                break
        return resposta

    def test_estrategia_equilibrada_resiste_a_varios_eventos(self):
        for semente in range(12):
            with self.subTest(semente=semente):
                resposta = self._jogar_partida(semente)
                self.assertEqual(resposta["cidade"]["status"], "concluido")
                self.assertGreater(resposta["cidade"]["dados"]["dinheiro"], 0)
                self.assertGreaterEqual(resposta["cidade"]["avaliacao_final"]["total"], 4000)


if __name__ == "__main__":
    unittest.main()
