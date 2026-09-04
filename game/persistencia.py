import json
import sqlite3
from pathlib import Path
from threading import RLock
from time import time

from .cidade import Cidade
from .jogo import JogoCidade


class RepositorioPartidas:
    """Armazena partidas independentes em SQLite usando apenas a biblioteca padrao."""

    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        self._bloqueio = RLock()
        self._criar_banco()

    def _conectar(self):
        conexao = sqlite3.connect(self.caminho, timeout=10)
        conexao.execute("PRAGMA journal_mode=WAL")
        conexao.execute("PRAGMA busy_timeout=10000")
        return conexao

    def _criar_banco(self):
        conexao = self._conectar()
        try:
            with conexao:
                conexao.execute(
                    """
                    CREATE TABLE IF NOT EXISTS partidas (
                        id TEXT PRIMARY KEY,
                        estado TEXT NOT NULL,
                        atualizado_em INTEGER NOT NULL
                    )
                    """
                )
        finally:
            conexao.close()

    def salvar(self, partida_id, jogo):
        conteudo = json.dumps(jogo.cidade.exportar_persistencia(), ensure_ascii=False, separators=(",", ":"))
        with self._bloqueio:
            conexao = self._conectar()
            try:
                with conexao:
                    conexao.execute(
                        "INSERT OR REPLACE INTO partidas (id, estado, atualizado_em) VALUES (?, ?, ?)",
                        (partida_id, conteudo, round(time())),
                    )
            finally:
                conexao.close()

    def carregar(self, partida_id):
        if not partida_id:
            return None
        with self._bloqueio:
            conexao = self._conectar()
            try:
                linha = conexao.execute("SELECT estado FROM partidas WHERE id = ?", (partida_id,)).fetchone()
            finally:
                conexao.close()
        if not linha:
            return None
        jogo = JogoCidade()
        jogo.cidade = Cidade.restaurar_persistencia(json.loads(linha[0]))
        return jogo

    def executar(self, partida_id, acao):
        """Executa uma alteracao atomica, inclusive com mais de um processo web."""
        with self._bloqueio:
            conexao = self._conectar()
            try:
                conexao.execute("BEGIN IMMEDIATE")
                linha = conexao.execute(
                    "SELECT estado FROM partidas WHERE id = ?",
                    (partida_id,),
                ).fetchone()
                if not linha:
                    conexao.rollback()
                    return None
                jogo = JogoCidade()
                jogo.cidade = Cidade.restaurar_persistencia(json.loads(linha[0]))
                resultado = acao(jogo)
                conteudo = json.dumps(
                    jogo.cidade.exportar_persistencia(),
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                conexao.execute(
                    "UPDATE partidas SET estado = ?, atualizado_em = ? WHERE id = ?",
                    (conteudo, round(time()), partida_id),
                )
                conexao.commit()
                return resultado
            except Exception:
                conexao.rollback()
                raise
            finally:
                conexao.close()

    def limpar_antigas(self, dias=45):
        limite = round(time()) - dias * 24 * 60 * 60
        with self._bloqueio:
            conexao = self._conectar()
            try:
                with conexao:
                    conexao.execute("DELETE FROM partidas WHERE atualizado_em < ?", (limite,))
            finally:
                conexao.close()
