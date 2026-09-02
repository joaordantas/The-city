from flask import Flask, jsonify, redirect, render_template, request, url_for

from game import JogoCidade


app = Flask(__name__)
jogo = JogoCidade()


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
    return jsonify(jogo.estado())


@app.post("/api/novo-jogo")
def novo_jogo():
    dados = request.get_json(silent=True) or {}
    prefeito = dados.get("prefeito", "").strip()
    if not prefeito:
        return jsonify({
            "sucesso": False,
            "mensagem": "Informe o nome do prefeito antes de iniciar.",
        }), 400

    return jsonify(jogo.novo_jogo(prefeito))


@app.post("/api/construir")
def construir():
    dados = request.get_json(silent=True) or {}
    construcao_id = dados.get("construcao_id")
    posicao = dados.get("posicao")
    return jsonify(jogo.construir(construcao_id, posicao))


@app.post("/api/mover")
def mover():
    dados = request.get_json(silent=True) or {}
    return jsonify(jogo.mover(dados.get("predio_id"), dados.get("posicao")))


@app.post("/api/demolir")
def demolir():
    dados = request.get_json(silent=True) or {}
    return jsonify(jogo.demolir(dados.get("predio_id")))


@app.post("/api/melhorar")
def melhorar():
    dados = request.get_json(silent=True) or {}
    return jsonify(jogo.melhorar(dados.get("predio_id")))


@app.post("/api/expandir")
def expandir():
    dados = request.get_json(silent=True) or {}
    return jsonify(jogo.expandir(dados.get("setor_id")))


@app.post("/api/remover-obstaculo")
def remover_obstaculo():
    dados = request.get_json(silent=True) or {}
    return jsonify(jogo.remover_obstaculo(dados.get("posicao")))


@app.post("/api/construir-estrada")
def construir_estrada():
    dados = request.get_json(silent=True) or {}
    return jsonify(jogo.construir_estrada(dados.get("posicao")))


@app.post("/api/logistica/entregar")
def entregar_pedido():
    return jsonify(jogo.entregar_pedido())


@app.post("/api/logistica/recusar")
def recusar_pedido():
    return jsonify(jogo.recusar_pedido())


@app.post("/api/projetos/investir")
def investir_projeto():
    dados = request.get_json(silent=True) or {}
    return jsonify(jogo.investir_projeto(dados.get("projeto_id")))


@app.post("/api/reiniciar")
def reiniciar():
    return jsonify(jogo.reiniciar())


@app.post("/api/imposto")
def alterar_imposto():
    dados = request.get_json(silent=True) or {}
    return jsonify(jogo.alterar_imposto(dados.get("tipo"), dados.get("direcao")))


@app.post("/api/evento/responder")
def responder_evento():
    dados = request.get_json(silent=True) or {}
    return jsonify(jogo.responder_evento(dados.get("escolha_id")))


@app.post("/api/proxima-rodada")
def proxima_rodada():
    dados = request.get_json(silent=True) or {}
    return jsonify(jogo.proxima_rodada(dados.get("rodada_esperada")))


if __name__ == "__main__":
    app.run(debug=True)
