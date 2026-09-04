import os
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

from werkzeug.serving import make_server

from app import app


EDGE = next((
    caminho for caminho in (
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    )
    if caminho.exists()
), None)


@unittest.skipUnless(
    os.environ.get("THE_CITY_BROWSER_TESTS") == "1" and EDGE,
    "Defina THE_CITY_BROWSER_TESTS=1 em uma maquina com Edge para executar o navegador real.",
)
class NavegadorRealTest(unittest.TestCase):
    def test_menu_carrega_jogo_e_renderiza_estado_inicial(self):
        servidor = make_server("127.0.0.1", 0, app)
        thread = threading.Thread(target=servidor.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as perfil:
                resultado = subprocess.run(
                    [
                        str(EDGE),
                        "--headless=new",
                        "--disable-gpu",
                        "--no-first-run",
                        f"--user-data-dir={perfil}",
                        "--virtual-time-budget=3000",
                        "--dump-dom",
                        f"http://127.0.0.1:{servidor.server_port}/jogo?prefeito=Navegador",
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=20,
                    check=True,
                )
            pagina = resultado.stdout
            self.assertIn('id="prefeito-atual">Navegador</strong>', pagina)
            self.assertIn('id="numero-rodada">Rodada 01/20</strong>', pagina)
            self.assertIn("Casa", pagina)
            self.assertIn('id="modal-tutorial-jogo" class="modal-jogo" aria-hidden="false"', pagina)
        finally:
            servidor.shutdown()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
