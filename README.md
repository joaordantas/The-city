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
game/eventos.py         Eventos, escolhas, efeitos e consequencias
game/missoes.py         Missoes data-driven e recompensas unicas
game/progressao.py      Fases, desbloqueios e Plano de Governo
game/crises.py          Alertas persistentes e derrota antecipada
game/avaliacao.py       Pontuacao e classificacao final
game/territorio.py      Setores, obstaculos, estradas e transito simples
game/producao.py        Producao automatica, consumo e limites de estoque
game/logistica.py       Pedidos opcionais e entregas atomicas
game/projetos.py        Grandes projetos por etapas e beneficios finais
game/jogo.py            Coordena os sistemas do jogo
templates/index.html    Menu inicial
templates/jogo.html     Interface da partida
static/css/style.css    Visual do jogo
static/js/game.js       Comunicacao com a API e atualizacao da tela
static/js/rodadas.js    Timer, pausa e encerramento das rodadas
static/js/sistemas-avancados.js  Interface de producao, logistica e projetos
static/js/cidade-viva.js         Carros e pedestres leves em Canvas
static/js/audio.js               Efeitos sonoros sintetizados com Web Audio
static/js/menu.js                Configuracoes e creditos do menu
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

## Progressao da partida

A partida possui 20 rodadas. Construcoes e sistemas sao liberados por fases,
as missoes mostram no maximo tres objetivos e os eventos pedem escolhas sem
pausar o timer. Efeitos temporarios duram rodadas, decisoes ignoradas recebem
uma consequencia automatica e crises persistentes podem encerrar o mandato.

A Prefeitura reune visao geral, Plano de Governo e historico estruturado. No
fim, sete areas recebem notas de 0 a 1000 para evitar que apenas o dinheiro
defina uma boa administracao.

## Expansao e producao

O mapa possui 36 terrenos organizados em quatro distritos. Novos setores sao
comprados uma unica vez, obstaculos podem ser removidos e predios sem acesso
viario sofrem uma penalidade visivel de eficiencia. O transito usa apenas
capacidade e demanda, sem busca de rotas.

Fazendas e fabricas produzem alimentos, materiais e mercadorias ao encerrar
cada rodada. Armazens ampliam o limite, comercios consomem mercadorias e a
disponibilidade de alimentos influencia crescimento e qualidade de vida.
Pedidos logisticos sao opcionais e grandes projetos ativam seus beneficios
somente depois da ultima etapa.
