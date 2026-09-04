import os
import secrets

from flask import Flask, jsonify, redirect, render_template, request, url_for

from game import JogoCidade
from game.persistencia import RepositorioPartidas


app = Flask(__name__)
jogo = JogoCidade()
repositorio = RepositorioPartidas(
    os.environ.get("THE_CITY_DB", os.path.join(app.instance_path, "partidas.sqlite3"))
)
repositorio.limpar_antigas()
COOKIE_PARTIDA = "the_city_partida"


def _dados_json():
    dados = request.get_json(silent=True)
    return dados if isinstance(dados, dict) else {}


def _partida_atual():
    partida_id = request.cookies.get(COOKIE_PARTIDA)
    partida = repositorio.carregar(partida_id)
    return partida_id, partida or jogo


def _executar_na_partida(acao, exige_rodada_ativa=True):
    partida_id = request.cookies.get(COOKIE_PARTIDA)
    if partida_id:
        def executar(partida):
            if exige_rodada_ativa:
                timer = partida.estado_timer()
                if timer["pausado"]:
                    return {
                        "sucesso": False,
                        "mensagem": "Retome o jogo antes de realizar esta acao.",
                        **partida.estado(),
                    }
                if timer["restante_ms"] <= 0:
                    return {
                        "sucesso": False,
                        "mensagem": "A rodada terminou e esta sendo processada.",
                        **partida.estado(),
                    }
            return acao(partida)

        resultado = repositorio.executar(partida_id, executar)
        if resultado is not None:
            return jsonify(resultado)
    # Mantem compatibilidade com execucao local e clientes antigos sem cookie.
    return jsonify(acao(jogo))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/jogo")
def pagina_jogo():
    prefeito = request.args.get("prefeito", "").strip()
    if not prefeito:
        return redirect(url_for("index"))

    return render_template("jogo.html")


@app.get("/api/estado")
def obter_estado():
    _, partida = _partida_atual()
    return jsonify(partida.estado())


@app.post("/api/novo-jogo")
def novo_jogo():
    dados = _dados_json()
    valor_prefeito = dados.get("prefeito", "")
    prefeito = valor_prefeito.strip() if isinstance(valor_prefeito, str) else ""
    if not prefeito:
        return jsonify({
            "sucesso": False,
            "mensagem": "Informe o nome do prefeito antes de iniciar.",
        }), 400

    partida = JogoCidade()
    estado = partida.novo_jogo(prefeito[:24])
    partida_id = secrets.token_urlsafe(24)
    repositorio.salvar(partida_id, partida)
    resposta = jsonify(estado)
    resposta.set_cookie(
        COOKIE_PARTIDA,
        partida_id,
        max_age=60 * 60 * 24 * 30,
        httponly=True,
        samesite="Lax",
        secure=request.is_secure,
    )
    return resposta


@app.post("/api/construir")
def construir():
    dados = _dados_json()
    construcao_id = dados.get("construcao_id")
    posicao = dados.get("posicao")
    return _executar_na_partida(lambda partida: partida.construir(construcao_id, posicao))


@app.post("/api/mover")
def mover():
    dados = _dados_json()
    return _executar_na_partida(lambda partida: partida.mover(dados.get("predio_id"), dados.get("posicao")))


@app.post("/api/demolir")
def demolir():
    dados = _dados_json()
    return _executar_na_partida(lambda partida: partida.demolir(dados.get("predio_id")))


@app.post("/api/melhorar")
def melhorar():
    dados = _dados_json()
    return _executar_na_partida(lambda partida: partida.melhorar(dados.get("predio_id")))


@app.post("/api/expandir")
def expandir():
    dados = _dados_json()
    return _executar_na_partida(lambda partida: partida.expandir(dados.get("setor_id")))


@app.post("/api/remover-obstaculo")
def remover_obstaculo():
    dados = _dados_json()
    return _executar_na_partida(lambda partida: partida.remover_obstaculo(dados.get("posicao")))


@app.post("/api/construir-estrada")
def construir_estrada():
    dados = _dados_json()
    return _executar_na_partida(lambda partida: partida.construir_estrada(dados.get("posicao")))


@app.post("/api/logistica/entregar")
def entregar_pedido():
    return _executar_na_partida(lambda partida: partida.entregar_pedido())


@app.post("/api/logistica/recusar")
def recusar_pedido():
    return _executar_na_partida(lambda partida: partida.recusar_pedido())


@app.post("/api/projetos/investir")
def investir_projeto():
    dados = _dados_json()
    return _executar_na_partida(lambda partida: partida.investir_projeto(dados.get("projeto_id")))


@app.post("/api/reiniciar")
def reiniciar():
    return _executar_na_partida(lambda partida: partida.reiniciar(), exige_rodada_ativa=False)


@app.post("/api/imposto")
def alterar_imposto():
    dados = _dados_json()
    return _executar_na_partida(lambda partida: partida.alterar_imposto(dados.get("tipo"), dados.get("direcao")))


@app.post("/api/evento/responder")
def responder_evento():
    dados = _dados_json()
    return _executar_na_partida(lambda partida: partida.responder_evento(dados.get("escolha_id")))


@app.post("/api/proxima-rodada")
def proxima_rodada():
    dados = _dados_json()
    return _executar_na_partida(
        lambda partida: partida.proxima_rodada(dados.get("rodada_esperada")),
        exige_rodada_ativa=False,
    )


@app.post("/api/timer/pausar")
def pausar_timer():
    return _executar_na_partida(lambda partida: partida.pausar_timer(), exige_rodada_ativa=False)


@app.post("/api/timer/retomar")
def retomar_timer():
    return _executar_na_partida(lambda partida: partida.retomar_timer(), exige_rodada_ativa=False)


if __name__ == "__main__":
    app.run(debug=True)
