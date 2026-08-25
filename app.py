from flask import Flask, jsonify, render_template, request

from game import JogoCidade


app = Flask(__name__)
jogo = JogoCidade()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/jogo")
def pagina_jogo():
    return render_template("jogo.html")


@app.get("/api/estado")
def obter_estado():
    return jsonify(jogo.estado())


@app.post("/api/novo-jogo")
def novo_jogo():
    dados = request.get_json(silent=True) or {}
    prefeito = dados.get("prefeito", "Prefeito")
    return jsonify(jogo.novo_jogo(prefeito))


@app.post("/api/construir")
def construir():
    dados = request.get_json(silent=True) or {}
    construcao_id = dados.get("construcao_id")
    posicao = dados.get("posicao")
    return jsonify(jogo.construir(construcao_id, posicao))


@app.post("/api/proxima-rodada")
def proxima_rodada():
    return jsonify(jogo.proxima_rodada())


if __name__ == "__main__":
    app.run(debug=True)
