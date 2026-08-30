# Cidade em Equilibrio

MVP de um jogo escolar de administracao de cidade.

O jogador e o prefeito e precisa equilibrar dinheiro, populacao, empregos,
educacao, saude, energia, agua, poluicao e qualidade de vida.

## Como rodar

1. Instale as dependencias:

```bash
pip install -r requirements.txt
```

2. Inicie o servidor:

```bash
python app.py
```

3. Abra no navegador:

```text
http://127.0.0.1:5000
```

## Testes

```bash
python -m unittest discover -s tests -p "test_*.py"
node tests/test_rodadas.mjs
```

## Estrutura principal

```text
app.py                  Servidor Flask e rotas da API
game/dados.py           Numeros iniciais e configuracoes
game/cidade.py          Estado atual da cidade
game/construcoes.py     Regras de construcao
game/economia.py        Receitas, despesas e rodadas
game/eventos.py         Eventos aleatorios
game/jogo.py            Coordena os sistemas do jogo
templates/index.html    Interface principal
static/css/style.css    Visual do jogo
static/js/game.js       Comunicacao com a API e atualizacao da tela
static/js/rodadas.js    Timer, pausa e encerramento das rodadas
```

## Organizacao

O projeto possui uma unica versao ativa: o Flask serve as paginas de
`templates/`, os arquivos visuais ficam em `static/` e as regras do jogo ficam
isoladas no pacote `game/`.

## Simulacao

As construcoes sao organizadas por categoria e posicionadas diretamente no
grid. Agua e energia usam capacidade, demanda e sobrecarga; a eficiencia dos
predios conecta esses recursos a empregos, servicos, receita e poluicao.

O painel de economia apresenta receitas, despesas, previsao da rodada e os
impostos residencial, comercial e industrial. Predios podem ser melhorados,
movidos e demolidos sem duplicar efeitos.
