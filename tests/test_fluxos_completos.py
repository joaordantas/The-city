import unittest
from unittest.mock import patch

from app import app, jogo as jogo_api
from game import JogoCidade
from game.dados import CONSTRUCOES, EVENTOS
from game.eventos import iniciar_evento, resolver_evento_ignorado


class FluxosCompletosTest(unittest.TestCase):
    def test_todas_as_construcoes_podem_ser_criadas_quando_desbloqueadas(self):
        for tipo, dados in CONSTRUCOES.items():
            with self.subTest(construcao=tipo):
                jogo = JogoCidade()
                jogo.novo_jogo(tipo)
                jogo.cidade.dados.update({"dinheiro": 100_000, "rodada": dados["rodada_desbloqueio"]})
                resposta = jogo.construir(tipo, 0)
                self.assertTrue(resposta["sucesso"], resposta["mensagem"])
                self.assertEqual(resposta["cidade"]["construcoes"][0]["tipo"], tipo)

    def test_todas_as_escolhas_de_eventos_e_omissoes_sao_processadas(self):
        for evento in EVENTOS:
            for escolha in evento["escolhas"]:
                with self.subTest(evento=evento["id"], escolha=escolha["id"]):
                    jogo = JogoCidade()
                    jogo.novo_jogo(evento["id"])
                    jogo.cidade.dados.update({"dinheiro": 100_000, "rodada": evento["rodada_inicio"]})
                    iniciar_evento(jogo.cidade, evento["id"])
                    resposta = jogo.responder_evento(escolha["id"])
                    self.assertTrue(resposta["sucesso"], resposta["mensagem"])
                    self.assertIsNone(resposta["cidade"]["evento_ativo"])

            with self.subTest(evento=evento["id"], escolha="omissao"):
                jogo = JogoCidade()
                jogo.novo_jogo(evento["id"])
                jogo.cidade.dados["rodada"] = evento["rodada_inicio"]
                iniciar_evento(jogo.cidade, evento["id"])
                resultado = resolver_evento_ignorado(jogo.cidade)
                self.assertEqual(resultado["id"], evento["id"])
                self.assertIsNone(jogo.cidade.evento_ativo)

    def test_segunda_casa_nao_reinicia_nem_repete_missao(self):
        jogo_api.novo_jogo("Regressao")
        cliente = app.test_client()

        primeira = cliente.post("/api/construir", json={"construcao_id": "casa", "posicao": 0}).get_json()
        segunda = cliente.post("/api/construir", json={"construcao_id": "casa", "posicao": 1}).get_json()

        self.assertEqual(primeira["cidade"]["dados"]["dinheiro"], 14600)
        self.assertEqual(segunda["cidade"]["dados"]["dinheiro"], 13700)
        self.assertEqual(segunda["cidade"]["dados"]["rodada"], 1)
        self.assertEqual(len(segunda["cidade"]["construcoes"]), 2)
        self.assertEqual({item["id"] for item in segunda["cidade"]["construcoes"]}, {"predio-1", "predio-2"})
        self.assertEqual(segunda["missoes"]["concluidas"].count("primeira_moradia"), 1)
        self.assertNotIn("Missao concluida", segunda["mensagem"])
        historico = [item for item in segunda["cidade"]["historico"] if item["tipo"] == "missao"]
        self.assertEqual(len(historico), 1)

    def _forcar_derrota(self, tipo):
        jogo = JogoCidade()
        jogo.novo_jogo(tipo)
        cidade = jogo.cidade
        if tipo == "financeira":
            cidade.dados["dinheiro"] = -100_000
        elif tipo == "social":
            cidade.modificadores.append({
                "id": "teste-social", "nome": "Teste social", "alvo": "qualidade_bonus",
                "valor": -100, "rodadas_restantes": 10,
            })
        else:
            cidade.modificadores.append({
                "id": "teste-infra", "nome": "Teste infraestrutura", "alvo": "capacidade_energia_pct",
                "valor": -90, "rodadas_restantes": 10,
            })

        with patch("game.jogo.sortear_evento", return_value=None):
            resposta = None
            for _ in range(3):
                resposta = jogo.proxima_rodada(cidade.dados["rodada"])
        return jogo, resposta

    def test_derrota_financeira_apos_tres_rodadas_criticas(self):
        _, resposta = self._forcar_derrota("financeira")
        self.assertEqual(resposta["cidade"]["status"], "derrota")
        self.assertEqual(resposta["cidade"]["motivo_fim"], "Crise financeira")
        self.assertEqual(resposta["crises"]["contadores"]["financeira"], 3)

    def test_derrota_social_apos_tres_rodadas_criticas(self):
        _, resposta = self._forcar_derrota("social")
        self.assertEqual(resposta["cidade"]["status"], "derrota")
        self.assertEqual(resposta["cidade"]["motivo_fim"], "Crise social")
        self.assertEqual(resposta["crises"]["contadores"]["social"], 3)

    def test_derrota_de_infraestrutura_apos_tres_rodadas_criticas(self):
        _, resposta = self._forcar_derrota("infraestrutura")
        self.assertEqual(resposta["cidade"]["status"], "derrota")
        self.assertEqual(resposta["cidade"]["motivo_fim"], "Colapso de infraestrutura")
        self.assertEqual(resposta["crises"]["contadores"]["infraestrutura"], 3)

    def test_acoes_ficam_bloqueadas_depois_da_derrota(self):
        jogo, _ = self._forcar_derrota("financeira")
        dinheiro = jogo.cidade.dados["dinheiro"]
        resposta = jogo.construir("casa", 0)
        self.assertFalse(resposta["sucesso"])
        self.assertEqual(resposta["mensagem"], "A partida ja terminou.")
        self.assertEqual(resposta["cidade"]["dados"]["dinheiro"], dinheiro)
        self.assertEqual(resposta["cidade"]["construcoes"], [])

    def test_recuperacao_antes_do_limite_evitar_derrota(self):
        jogo = JogoCidade()
        jogo.novo_jogo("Recuperacao")
        jogo.cidade.dados["dinheiro"] = -100_000
        with patch("game.jogo.sortear_evento", return_value=None):
            jogo.proxima_rodada(1)
            jogo.proxima_rodada(2)
            jogo.cidade.dados["dinheiro"] = 10_000
            resposta = jogo.proxima_rodada(3)
        self.assertEqual(resposta["cidade"]["status"], "jogando")
        self.assertEqual(resposta["crises"]["contadores"]["financeira"], 0)
        self.assertEqual(resposta["crises"]["resolvidas"], 1)

    def test_vitoria_com_cidade_equilibrada_encerra_na_rodada_20(self):
        jogo = JogoCidade()
        jogo.novo_jogo("Vitoria")
        cidade = jogo.cidade
        cidade.dados.update({"dinheiro": 200_000, "rodada": 13})
        cidade.setores_desbloqueados.update({"norte", "industrial", "rural"})
        cidade.obstaculos.clear()
        plano = [
            ("casa", 0), ("casa", 1), ("hospital", 2), ("hospital", 3),
            ("escola", 4), ("escola", 5), ("comercio", 6), ("fabrica", 11),
            ("estacao_agua", 12), ("usina_solar", 17), ("parque", 18),
            ("fazenda", 23), ("armazem", 24),
        ]
        for tipo, posicao in plano:
            self.assertTrue(jogo.construir(tipo, posicao)["sucesso"])
        cidade.dados["rodada"] = 1
        cidade.marcar_simulacao_suja()

        with patch("game.jogo.sortear_evento", return_value=None):
            for rodada in range(1, 21):
                resposta = jogo.proxima_rodada(rodada)

        self.assertEqual(resposta["cidade"]["status"], "concluido")
        self.assertEqual(resposta["cidade"]["dados"]["rodada"], 20)
        self.assertEqual(len(resposta["cidade"]["historico_metricas"]), 20)
        self.assertIn(
            resposta["cidade"]["avaliacao_final"]["classificacao"],
            {"Cidade equilibrada", "Gestao excelente", "Gestao excepcional"},
        )
        self.assertGreaterEqual(resposta["cidade"]["avaliacao_final"]["total"], 4000)

    def test_clientes_recebem_partidas_independentes_e_persistentes(self):
        cliente_a = app.test_client()
        cliente_b = app.test_client()
        inicio_a = cliente_a.post("/api/novo-jogo", json={"prefeito": "Ana"}).get_json()
        inicio_b = cliente_b.post("/api/novo-jogo", json={"prefeito": "Bia"}).get_json()
        self.assertEqual(inicio_a["cidade"]["prefeito"], "Ana")
        self.assertEqual(inicio_b["cidade"]["prefeito"], "Bia")

        cliente_a.post("/api/timer/retomar", json={})
        cliente_a.post("/api/construir", json={"construcao_id": "casa", "posicao": 0})
        estado_a = cliente_a.get("/api/estado").get_json()
        estado_b = cliente_b.get("/api/estado").get_json()
        self.assertEqual(len(estado_a["cidade"]["construcoes"]), 1)
        self.assertEqual(estado_b["cidade"]["construcoes"], [])

    def test_api_bloqueia_todas_as_acoes_enquanto_o_jogo_esta_pausado(self):
        cliente = app.test_client()
        cliente.post("/api/novo-jogo", json={"prefeito": "Pausa"})
        respostas = [
            cliente.post("/api/construir", json={"construcao_id": "casa", "posicao": 0}),
            cliente.post("/api/construir-estrada", json={"posicao": 0}),
            cliente.post("/api/expandir", json={"setor_id": "norte"}),
            cliente.post("/api/projetos/investir", json={"projeto_id": "parque_central"}),
        ]
        self.assertTrue(all(not resposta.get_json()["sucesso"] for resposta in respostas))
        self.assertTrue(all("Retome" in resposta.get_json()["mensagem"] for resposta in respostas))

    def test_timer_da_api_pausa_e_retorna_sem_reiniciar(self):
        cliente = app.test_client()
        inicio = cliente.post("/api/novo-jogo", json={"prefeito": "Tempo"}).get_json()
        self.assertTrue(inicio["timer"]["pausado"])
        rodando = cliente.post("/api/timer/retomar", json={}).get_json()
        self.assertFalse(rodando["timer"]["pausado"])
        pausado = cliente.post("/api/timer/pausar", json={}).get_json()
        self.assertTrue(pausado["timer"]["pausado"])
        self.assertLessEqual(pausado["timer"]["restante_ms"], 60_000)
        recarregado = cliente.get("/api/estado").get_json()
        self.assertEqual(recarregado["timer"]["restante_ms"], pausado["timer"]["restante_ms"])

    def test_novo_jogo_rejeita_nome_que_nao_seja_texto(self):
        resposta = app.test_client().post("/api/novo-jogo", json={"prefeito": 123})
        self.assertEqual(resposta.status_code, 400)
        self.assertFalse(resposta.get_json()["sucesso"])

    def test_reinicio_so_acontece_quando_solicitado(self):
        jogo = JogoCidade()
        jogo.novo_jogo("Estado")
        primeira = jogo.construir("casa", 0)
        segunda = jogo.construir("casa", 1)
        self.assertEqual(len(segunda["cidade"]["construcoes"]), 2)
        reiniciado = jogo.reiniciar()
        self.assertEqual(reiniciado["cidade"]["construcoes"], [])
        self.assertEqual(reiniciado["cidade"]["dados"]["dinheiro"], 15_000)
        self.assertEqual(reiniciado["missoes"]["concluidas"], [])


if __name__ == "__main__":
    unittest.main()
