DADOS_INICIAIS = {
    "dinheiro": 15000,
    "populacao": 100,
    "capacidade_populacional": 140,
    "empregos": 30,
    "educacao": 50,
    "saude": 50,
    "energia": 50,
    "agua": 75,
    "poluicao": 10,
    "qualidade_vida": 50,
    "rodada": 1,
    "max_rodadas": 20,
}

CONFIG_RODADAS = {
    "duracoes": [
        {"inicio": 1, "fim": 2, "tempo": 60},
        {"inicio": 3, "fim": 5, "tempo": 60},
        {"inicio": 6, "fim": 10, "tempo": 55},
        {"inicio": 11, "fim": 15, "tempo": 50},
        {"inicio": 16, "fim": 20, "tempo": 45},
    ],
    "duracao_resumo": 3,
}

CONFIG_IMPOSTOS = {
    "minimo": 4,
    "maximo": 20,
    "passo": 1,
    "taxas_iniciais": {"residencial": 12, "comercio": 12, "industria": 12},
    "base_residencial_por_habitante": 50,
    "outras_receitas": 300,
    "taxa_neutra": 12,
    "impacto_qualidade_por_ponto": 0.4,
    "impacto_crescimento_por_ponto": 0.03,
}

CONFIG_SIMULACAO = {
    "capacidade_base_energia": 100,
    "capacidade_base_agua": 100,
    "demanda_energia_por_habitante": 0.5,
    "demanda_agua_por_habitante": 0.75,
    "capacidade_base_saude": 50,
    "capacidade_base_educacao": 50,
    "demanda_saude_por_habitante": 1,
    "demanda_educacao_por_habitante": 1,
    "empregos_base": 30,
    "proporcao_populacao_ativa": 0.6,
    "poluicao_base": 10,
    "custo_servicos_por_habitante": 6,
    "crescimento_populacional_base": 3,
    "pesos_qualidade_vida": {
        "saude": 0.25,
        "educacao": 0.20,
        "emprego": 0.15,
        "agua": 0.15,
        "energia": 0.15,
        "ambiente": 0.10,
    },
    "reembolso_demolicao": 0.4,
}

CONFIG_UPGRADES = {
    1: {
        "beneficio": 1,
        "consumo": 1,
        "manutencao": 1,
        "custo_upgrade": 0.6,
    },
    2: {
        "beneficio": 1.5,
        "consumo": 1.3,
        "manutencao": 1.45,
        "custo_upgrade": 0.9,
    },
    3: {
        "beneficio": 2.1,
        "consumo": 1.75,
        "manutencao": 2.05,
        "custo_upgrade": None,
    },
}

CATEGORIAS_CONSTRUCOES = {
    "residencial": "Residencial",
    "comercio": "Comercio",
    "industria": "Industria",
    "educacao": "Educacao",
    "saude": "Saude",
    "infraestrutura": "Infraestrutura",
    "lazer": "Lazer",
    "ambiental": "Ambiental",
    "especial": "Especial",
    "rural": "Rural",
}

CONSTRUCOES = {
    "casa": {
        "nome": "Casa",
        "categoria": "residencial",
        "custo": 900,
        "manutencao": 20,
        "capacidade_populacional": 25,
        "empregos": 0,
        "consumo_energia": 3,
        "consumo_agua": 4,
        "beneficio_principal": "+25 de capacidade residencial",
        "rodada_desbloqueio": 1,
    },
    "escola": {
        "nome": "Escola",
        "categoria": "educacao",
        "custo": 2000,
        "manutencao": 110,
        "empregos": 5,
        "capacidade_educacao": 22,
        "consumo_energia": 4,
        "consumo_agua": 3,
        "beneficio_principal": "+22 vagas de educacao",
        "rodada_desbloqueio": 6,
    },
    "hospital": {
        "nome": "Hospital",
        "categoria": "saude",
        "custo": 2800,
        "manutencao": 150,
        "empregos": 8,
        "capacidade_saude": 22,
        "consumo_energia": 6,
        "consumo_agua": 5,
        "beneficio_principal": "+22 de atendimento em saude",
        "rodada_desbloqueio": 6,
    },
    "parque": {
        "nome": "Parque",
        "categoria": "lazer",
        "custo": 1200,
        "manutencao": 45,
        "empregos": 0,
        "poluicao": -8,
        "qualidade_bonus": 3,
        "beneficio_principal": "+3 de bem-estar e -8 de poluicao",
        "rodada_desbloqueio": 1,
    },
    "comercio": {
        "nome": "Comercio",
        "categoria": "comercio",
        "custo": 1600,
        "manutencao": 70,
        "empregos": 14,
        "consumo_energia": 5,
        "consumo_agua": 3,
        "atividade_economica": 1600,
        "beneficio_principal": "+14 empregos e receita comercial",
        "rodada_desbloqueio": 3,
        "consumo_estoque": {"mercadorias": 8},
    },
    "fabrica": {
        "nome": "Fabrica",
        "categoria": "industria",
        "custo": 2600,
        "manutencao": 130,
        "empregos": 28,
        "consumo_energia": 12,
        "consumo_agua": 8,
        "poluicao": 12,
        "atividade_economica": 4000,
        "beneficio_principal": "+28 empregos e receita industrial",
        "rodada_desbloqueio": 9,
        "producao": {"materiais": 20, "mercadorias": 22},
    },
    "estacao_agua": {
        "nome": "Estacao de agua",
        "categoria": "infraestrutura",
        "custo": 2200,
        "manutencao": 95,
        "empregos": 4,
        "gera_agua": 40,
        "consumo_energia": 2,
        "capacidade_saude": 3,
        "beneficio_principal": "+40 de capacidade de agua",
        "rodada_desbloqueio": 3,
    },
    "usina_solar": {
        "nome": "Usina solar",
        "categoria": "ambiental",
        "custo": 2400,
        "manutencao": 75,
        "empregos": 4,
        "gera_energia": 30,
        "consumo_agua": 1,
        "poluicao": -2,
        "beneficio_principal": "+30 de capacidade de energia",
        "rodada_desbloqueio": 3,
    },
    "fazenda": {
        "nome": "Fazenda urbana",
        "categoria": "rural",
        "custo": 1800,
        "manutencao": 60,
        "empregos": 6,
        "consumo_energia": 2,
        "consumo_agua": 5,
        "producao": {"alimentos": 25},
        "beneficio_principal": "+25 alimentos por rodada",
        "rodada_desbloqueio": 6,
    },
    "armazem": {
        "nome": "Armazem",
        "categoria": "infraestrutura",
        "custo": 1700,
        "manutencao": 50,
        "empregos": 4,
        "consumo_energia": 2,
        "capacidade_estoque": 200,
        "beneficio_principal": "+200 de capacidade no estoque",
        "rodada_desbloqueio": 6,
    },
    "centro_distribuicao": {
        "nome": "Centro de distribuicao",
        "categoria": "especial",
        "custo": 3800,
        "manutencao": 130,
        "empregos": 12,
        "consumo_energia": 6,
        "consumo_agua": 2,
        "capacidade_estoque": 350,
        "limite": 1,
        "beneficio_principal": "+350 de estoque e apoio logistico",
        "rodada_desbloqueio": 9,
    },
    "praca": {
        "nome": "Praca",
        "categoria": "lazer",
        "custo": 600,
        "manutencao": 20,
        "empregos": 0,
        "poluicao": -1,
        "qualidade_bonus": 2,
        "limite": 4,
        "beneficio_principal": "+2 de bem-estar e -1 de poluicao",
        "rodada_desbloqueio": 3,
    },
    "arvore": {
        "nome": "Area arborizada",
        "categoria": "ambiental",
        "custo": 100,
        "manutencao": 0,
        "empregos": 0,
        "poluicao": -1,
        "limite": 8,
        "beneficio_principal": "Pequena reducao de poluicao",
        "rodada_desbloqueio": 3,
    },
}

CONFIG_MAPA = {
    "colunas": 6,
    "total_celulas": 36,
    "setor_inicial": "centro",
    "custo_estrada": 100,
    "penalidade_sem_acesso": 0.70,
    "capacidade_viaria_base": 45,
    "capacidade_por_estrada": 16,
    "demanda_por_habitante": 0.35,
    "setores": {
        "centro": {"nome": "Centro", "custo": 0, "celulas": list(range(16)), "distrito": "Centro"},
        "norte": {"nome": "Setor Norte", "custo": 2800, "celulas": list(range(16, 24)), "distrito": "Zona Residencial"},
        "industrial": {"nome": "Setor Industrial", "custo": 3500, "celulas": list(range(24, 30)), "distrito": "Zona Industrial"},
        "rural": {"nome": "Setor Rural", "custo": 3000, "celulas": list(range(30, 36)), "distrito": "Zona Rural"},
    },
    "obstaculos": {
        18: {"tipo": "arvores", "nome": "Arvores densas", "custo_remocao": 250},
        26: {"tipo": "pedras", "nome": "Pedras", "custo_remocao": 300},
        33: {"tipo": "entulho", "nome": "Entulho", "custo_remocao": 200},
    },
}

CONFIG_PRODUCAO = {
    "recursos": ("alimentos", "materiais", "mercadorias"),
    "estoque_inicial": {"alimentos": 0, "materiais": 0, "mercadorias": 0},
    "capacidade_base": 100,
    "abastecimento_externo_alimentos": 10,
    "demanda_alimentos_por_habitante": 0.10,
    "fator_minimo_comercio": 0.35,
    "penalidade_qualidade_falta_alimentos": 6,
}

PEDIDOS_LOGISTICOS = [
    {"id": "pedido_bairro", "titulo": "Abastecer cidades vizinhas", "rodada_inicio": 9, "rodada_fim": 12, "recursos": {"alimentos": 30, "materiais": 20}, "recompensa": 2200},
    {"id": "pedido_obras", "titulo": "Consorcio regional de obras", "rodada_inicio": 13, "rodada_fim": 16, "recursos": {"materiais": 50, "mercadorias": 25}, "recompensa": 3800},
    {"id": "pedido_final", "titulo": "Feira metropolitana", "rodada_inicio": 17, "rodada_fim": 20, "recursos": {"alimentos": 45, "materiais": 35, "mercadorias": 45}, "recompensa": 5200},
]

PROJETOS_ESPECIAIS = {
    "usina_municipal": {
        "nome": "Usina solar municipal", "rodada_desbloqueio": 13,
        "descricao": "Grande capacidade energetica com menor impacto ambiental.",
        "etapas": [{"dinheiro": 1400, "materiais": 20}, {"dinheiro": 2000, "materiais": 35}, {"dinheiro": 2600, "materiais": 50}],
        "efeitos": {"gera_energia": 60, "poluicao": -4},
    },
    "universidade": {
        "nome": "Universidade Estadual", "rodada_desbloqueio": 13,
        "descricao": "Educacao avancada, empregos e atratividade.",
        "etapas": [{"dinheiro": 1800, "materiais": 25}, {"dinheiro": 2400, "materiais": 40}, {"dinheiro": 3000, "materiais": 55}],
        "efeitos": {"capacidade_educacao": 35, "empregos": 15, "qualidade_bonus": 3, "consumo_energia": 8, "consumo_agua": 5},
    },
    "parque_central": {
        "nome": "Parque Central", "rodada_desbloqueio": 13,
        "descricao": "Estrutura ambiental permanente para toda a cidade.",
        "etapas": [{"dinheiro": 1200, "materiais": 15}, {"dinheiro": 1800, "materiais": 25}, {"dinheiro": 2400, "materiais": 35}],
        "efeitos": {"poluicao": -10, "qualidade_bonus": 8},
    },
}

CONFIG_PROGRESSAO = {
    "fases": [
        {"inicio": 1, "fim": 2, "nome": "Fundacao", "intensidade_eventos": 0},
        {"inicio": 3, "fim": 5, "nome": "Crescimento", "intensidade_eventos": 0.55},
        {"inicio": 6, "fim": 8, "nome": "Servicos publicos", "intensidade_eventos": 0.70},
        {"inicio": 9, "fim": 12, "nome": "Gestao complexa", "intensidade_eventos": 0.82},
        {"inicio": 13, "fim": 16, "nome": "Crises combinadas", "intensidade_eventos": 0.92},
        {"inicio": 17, "fim": 20, "nome": "Reta final", "intensidade_eventos": 1},
    ],
    "sistemas": {
        "missoes": 1,
        "eventos": 3,
        "prefeitura": 1,
        "impostos": 9,
        "upgrades": 13,
        "estradas": 3,
        "expansao": 6,
        "producao": 6,
        "logistica": 9,
        "projetos": 13,
    },
}

MISSOES = [
    {"id": "primeira_moradia", "titulo": "Um teto para comecar", "descricao": "Construa 1 Casa.", "tipo": "construcao", "rodada_inicio": 1, "rodada_fim": 5, "alvo": {"tipo": "casa", "valor": 1}, "recompensa": {"dinheiro": 500, "progresso": 100}},
    {"id": "bairro_verde", "titulo": "Primeiro bairro verde", "descricao": "Mantenha a poluicao em no maximo 5%.", "tipo": "indicador", "rodada_inicio": 1, "rodada_fim": 5, "alvo": {"campo": "poluicao", "operador": "<=", "valor": 5}, "recompensa": {"dinheiro": 450, "progresso": 90}},
    {"id": "crescer_110", "titulo": "Cidade em crescimento", "descricao": "Alcance 110 habitantes.", "tipo": "populacao", "rodada_inicio": 1, "rodada_fim": 8, "alvo": {"valor": 110}, "recompensa": {"dinheiro": 550, "progresso": 100}},
    {"id": "empregos_45", "titulo": "Novas oportunidades", "descricao": "Ofereca pelo menos 45 empregos.", "tipo": "empregos", "rodada_inicio": 3, "rodada_fim": 10, "alvo": {"valor": 45}, "recompensa": {"dinheiro": 600, "progresso": 120}},
    {"id": "agua_segura", "titulo": "Reservatorios seguros", "descricao": "Mantenha a utilizacao de agua em ate 80%.", "tipo": "infraestrutura", "rodada_inicio": 3, "rodada_fim": 12, "alvo": {"recurso": "agua", "valor": 80}, "recompensa": {"dinheiro": 650, "progresso": 120}},
    {"id": "saude_60", "titulo": "Saude para todos", "descricao": "Alcance 60% de cobertura de saude.", "tipo": "servico", "rodada_inicio": 6, "rodada_fim": 14, "alvo": {"campo": "saude", "valor": 60}, "recompensa": {"dinheiro": 750, "progresso": 140}},
    {"id": "educacao_60", "titulo": "Educacao que transforma", "descricao": "Alcance 60% de cobertura de educacao.", "tipo": "servico", "rodada_inicio": 6, "rodada_fim": 14, "alvo": {"campo": "educacao", "valor": 60}, "recompensa": {"dinheiro": 750, "progresso": 140}},
    {"id": "saldo_positivo", "titulo": "Contas equilibradas", "descricao": "Encerre uma rodada com resultado positivo.", "tipo": "saldo_positivo", "rodada_inicio": 9, "rodada_fim": 18, "alvo": {"valor": 1}, "recompensa": {"dinheiro": 800, "progresso": 160}},
    {"id": "baixa_poluicao", "titulo": "Ar respiravel", "descricao": "Mantenha a poluicao em ate 15%.", "tipo": "poluicao", "rodada_inicio": 9, "rodada_fim": 18, "alvo": {"valor": 15}, "recompensa": {"dinheiro": 700, "progresso": 150}},
    {"id": "cidade_eficiente", "titulo": "Cidade eficiente", "descricao": "Mantenha todos os predios com pelo menos 90% de eficiencia.", "tipo": "eficiencia", "rodada_inicio": 13, "rodada_fim": 20, "alvo": {"valor": 90}, "recompensa": {"dinheiro": 900, "progresso": 200}},
    {"id": "superar_crise", "titulo": "Resposta a crise", "descricao": "Supere pelo menos uma crise antes que ela encerre o mandato.", "tipo": "sobreviver_crise", "rodada_inicio": 13, "rodada_fim": 20, "alvo": {"valor": 1}, "recompensa": {"dinheiro": 1000, "progresso": 220}},
]

EVENTOS = [
    {
        "id": "seca", "titulo": "Seca prolongada", "descricao": "Os reservatorios baixaram e a cidade precisa escolher uma resposta.",
        "rodada_inicio": 3, "chance": 18, "cooldown": 4,
        "condicoes": [{"campo": "agua", "operador": ">=", "valor": 70}],
        "escolhas": [
            {"id": "racionar", "titulo": "Adotar racionamento", "descricao": "Poupa agua, mas reduz o bem-estar por 2 rodadas.", "efeitos": [{"tipo": "modificador", "alvo": "demanda_agua_pct", "valor": -18, "duracao": 2, "nome": "Racionamento"}, {"tipo": "modificador", "alvo": "qualidade_bonus", "valor": -4, "duracao": 2, "nome": "Restricoes de agua"}]},
            {"id": "obras", "titulo": "Obras emergenciais", "descricao": "Investe no abastecimento temporario.", "efeitos": [{"tipo": "dinheiro", "valor": -700}, {"tipo": "modificador", "alvo": "capacidade_agua_pct", "valor": 20, "duracao": 2, "nome": "Abastecimento emergencial"}]},
        ],
        "ignorado": [{"tipo": "dinheiro", "valor": -450}, {"tipo": "modificador", "alvo": "capacidade_agua_pct", "valor": -12, "duracao": 2, "nome": "Reservatorios vazios"}],
    },
    {
        "id": "feira_empregos", "titulo": "Feira de empregos", "descricao": "Empresarios querem apoio para abrir vagas.",
        "rodada_inicio": 3, "chance": 15, "cooldown": 4,
        "condicoes": [{"campo": "taxa_desemprego", "operador": ">=", "valor": 25}],
        "escolhas": [
            {"id": "incentivo", "titulo": "Dar incentivo", "descricao": "Custa agora e fortalece comercio e industria por 3 rodadas.", "efeitos": [{"tipo": "dinheiro", "valor": -350}, {"tipo": "modificador", "alvo": "eficiencia_economica_pct", "valor": 18, "duracao": 3, "nome": "Incentivo empresarial"}]},
            {"id": "capacitar", "titulo": "Capacitar moradores", "descricao": "Melhora a ocupacao das vagas por 3 rodadas.", "efeitos": [{"tipo": "dinheiro", "valor": -500}, {"tipo": "modificador", "alvo": "empregos_bonus", "valor": 10, "duracao": 3, "nome": "Programa de capacitacao"}]},
        ],
        "ignorado": [{"tipo": "modificador", "alvo": "qualidade_bonus", "valor": -3, "duracao": 2, "nome": "Frustracao dos desempregados"}],
    },
    {
        "id": "epidemia", "titulo": "Surto de gripe", "descricao": "A rede de saude esta sob pressao.",
        "rodada_inicio": 6, "chance": 14, "cooldown": 5,
        "condicoes": [{"campo": "saude", "operador": "<=", "valor": 75}],
        "escolhas": [
            {"id": "campanha", "titulo": "Campanha de prevencao", "descricao": "Eleva a cobertura de saude por 2 rodadas.", "efeitos": [{"tipo": "dinheiro", "valor": -500}, {"tipo": "modificador", "alvo": "saude_bonus", "valor": 15, "duracao": 2, "nome": "Campanha de prevencao"}]},
            {"id": "emergencia", "titulo": "Abrir leitos emergenciais", "descricao": "Resposta forte, com custo alto.", "efeitos": [{"tipo": "dinheiro", "valor": -850}, {"tipo": "modificador", "alvo": "saude_bonus", "valor": 25, "duracao": 1, "nome": "Leitos emergenciais"}]},
        ],
        "ignorado": [{"tipo": "modificador", "alvo": "saude_bonus", "valor": -18, "duracao": 2, "nome": "Surto sem resposta"}, {"tipo": "futuro", "apos_rodadas": 2, "titulo": "Conta hospitalar atrasada", "efeitos": [{"tipo": "dinheiro", "valor": -800}]}],
    },
    {
        "id": "protestos", "titulo": "Protestos na prefeitura", "descricao": "Moradores exigem respostas para a queda no bem-estar.",
        "rodada_inicio": 9, "chance": 16, "cooldown": 4,
        "condicoes": [{"campo": "qualidade_vida", "operador": "<=", "valor": 55}],
        "escolhas": [
            {"id": "dialogar", "titulo": "Abrir dialogo", "descricao": "Custa recursos e recupera confianca.", "efeitos": [{"tipo": "dinheiro", "valor": -300}, {"tipo": "modificador", "alvo": "qualidade_bonus", "valor": 6, "duracao": 2, "nome": "Dialogo comunitario"}]},
            {"id": "manter_plano", "titulo": "Manter o plano", "descricao": "Poupa caixa, mas aumenta a insatisfacao.", "efeitos": [{"tipo": "modificador", "alvo": "qualidade_bonus", "valor": -5, "duracao": 2, "nome": "Insatisfacao popular"}]},
        ],
        "ignorado": [{"tipo": "modificador", "alvo": "qualidade_bonus", "valor": -9, "duracao": 2, "nome": "Protestos ignorados"}],
    },
    {
        "id": "tempestade", "titulo": "Tempestade severa", "descricao": "A infraestrutura sofreu danos e exige uma decisao.",
        "rodada_inicio": 13, "chance": 18, "cooldown": 5,
        "condicoes": [],
        "escolhas": [
            {"id": "reparar", "titulo": "Reparar imediatamente", "descricao": "Evita perda de capacidade.", "efeitos": [{"tipo": "dinheiro", "valor": -900}]},
            {"id": "parcelar", "titulo": "Parcelar os reparos", "descricao": "Custa menos agora, mas reduz agua e energia por 2 rodadas.", "efeitos": [{"tipo": "dinheiro", "valor": -350}, {"tipo": "modificador", "alvo": "capacidade_agua_pct", "valor": -10, "duracao": 2, "nome": "Reparos lentos"}, {"tipo": "modificador", "alvo": "capacidade_energia_pct", "valor": -10, "duracao": 2, "nome": "Reparos lentos"}]},
        ],
        "ignorado": [{"tipo": "modificador", "alvo": "capacidade_agua_pct", "valor": -18, "duracao": 3, "nome": "Rede danificada"}, {"tipo": "modificador", "alvo": "capacidade_energia_pct", "valor": -18, "duracao": 3, "nome": "Rede danificada"}],
    },
]

PLANO_GOVERNO = [
    {"id": "populacao", "titulo": "Cidade viva", "descricao": "Terminar com 145 habitantes.", "campo": "populacao", "operador": ">=", "valor": 145},
    {"id": "saude", "titulo": "Saude digna", "descricao": "Terminar com saude em 60%.", "campo": "saude", "operador": ">=", "valor": 60},
    {"id": "educacao", "titulo": "Educacao forte", "descricao": "Terminar com educacao em 60%.", "campo": "educacao", "operador": ">=", "valor": 60},
    {"id": "ambiente", "titulo": "Cidade limpa", "descricao": "Terminar com poluicao em ate 20%.", "campo": "poluicao", "operador": "<=", "valor": 20},
    {"id": "qualidade", "titulo": "Bem-estar", "descricao": "Terminar com qualidade de vida em 55%.", "campo": "qualidade_vida", "operador": ">=", "valor": 55},
]

CONFIG_CRISES = {
    "rodadas_para_derrota": 3,
    "tipos": {
        "financeira": {"titulo": "Crise financeira", "campo": "dinheiro", "operador": "<", "valor": 0},
        "social": {"titulo": "Crise social", "campo": "qualidade_vida", "operador": "<=", "valor": 20},
        "infraestrutura": {"titulo": "Colapso de infraestrutura", "campo": "maior_utilizacao", "operador": ">=", "valor": 125},
    },
}

CONFIG_AVALIACAO = {
    "pesos": {"economia": 1, "saude": 1, "educacao": 1, "emprego": 1, "ambiente": 1, "qualidade": 1, "gestao": 1},
    "classificacoes": [
        {"minimo": 6000, "nome": "Gestao excepcional"},
        {"minimo": 5000, "nome": "Gestao excelente"},
        {"minimo": 4000, "nome": "Cidade equilibrada"},
        {"minimo": 3000, "nome": "Gestao instavel"},
        {"minimo": 0, "nome": "Cidade em crise"},
    ],
}


def dados_construcao_nivel(tipo, nivel):
    base = CONSTRUCOES[tipo]
    config = CONFIG_UPGRADES[nivel]
    dados = {**base, "tipo": tipo, "nivel": nivel}
    beneficios = (
        "capacidade_populacional", "empregos", "gera_agua", "gera_energia",
        "capacidade_saude", "capacidade_educacao", "atividade_economica", "poluicao",
        "capacidade_estoque", "qualidade_bonus",
    )
    consumos = ("consumo_agua", "consumo_energia")
    for chave in beneficios:
        dados[chave] = round(base.get(chave, 0) * config["beneficio"])
    for chave in consumos:
        dados[chave] = round(base.get(chave, 0) * config["consumo"])
    dados["manutencao"] = round(base["manutencao"] * config["manutencao"])
    dados["producao"] = {
        recurso: round(valor * config["beneficio"])
        for recurso, valor in base.get("producao", {}).items()
    }
    dados["consumo_estoque"] = dict(base.get("consumo_estoque", {}))
    proximo = CONFIG_UPGRADES.get(nivel + 1)
    dados["custo_upgrade"] = round(base["custo"] * config["custo_upgrade"]) if proximo else None
    return dados
