DADOS_INICIAIS = {
    "dinheiro": 10000,
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
        {"inicio": 3, "fim": 5, "tempo": 50},
        {"inicio": 6, "fim": 10, "tempo": 45},
        {"inicio": 11, "fim": 15, "tempo": 40},
        {"inicio": 16, "fim": 20, "tempo": 35},
    ],
    "duracao_resumo": 4,
}

CONFIG_IMPOSTOS = {
    "minimo": 4,
    "maximo": 20,
    "passo": 1,
    "taxas_iniciais": {"residencial": 12, "comercio": 12, "industria": 12},
    "base_residencial_por_habitante": 35,
    "outras_receitas": 240,
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
    "custo_servicos_por_habitante": 9,
    "crescimento_populacional_base": 3,
    "rodadas_em_crise_para_derrota": 3,
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
}

CONSTRUCOES = {
    "casa": {
        "nome": "Casa",
        "categoria": "residencial",
        "custo": 900,
        "manutencao": 25,
        "capacidade_populacional": 25,
        "empregos": 0,
        "consumo_energia": 3,
        "consumo_agua": 4,
        "beneficio_principal": "+25 de capacidade residencial",
    },
    "escola": {
        "nome": "Escola",
        "categoria": "educacao",
        "custo": 2000,
        "manutencao": 160,
        "empregos": 5,
        "capacidade_educacao": 8,
        "consumo_energia": 4,
        "consumo_agua": 3,
        "beneficio_principal": "+8 vagas de educacao",
    },
    "hospital": {
        "nome": "Hospital",
        "categoria": "saude",
        "custo": 2800,
        "manutencao": 230,
        "empregos": 8,
        "capacidade_saude": 10,
        "consumo_energia": 6,
        "consumo_agua": 5,
        "beneficio_principal": "+10 de atendimento em saude",
    },
    "parque": {
        "nome": "Parque",
        "categoria": "lazer",
        "custo": 1200,
        "manutencao": 70,
        "empregos": 0,
        "poluicao": -8,
        "beneficio_principal": "-8 de poluicao",
    },
    "comercio": {
        "nome": "Comercio",
        "categoria": "comercio",
        "custo": 1600,
        "manutencao": 90,
        "empregos": 14,
        "consumo_energia": 5,
        "consumo_agua": 3,
        "atividade_economica": 850,
        "beneficio_principal": "+14 empregos e receita comercial",
    },
    "fabrica": {
        "nome": "Fabrica",
        "categoria": "industria",
        "custo": 2600,
        "manutencao": 180,
        "empregos": 28,
        "consumo_energia": 12,
        "consumo_agua": 8,
        "poluicao": 12,
        "atividade_economica": 1800,
        "beneficio_principal": "+28 empregos e receita industrial",
    },
    "estacao_agua": {
        "nome": "Estacao de agua",
        "categoria": "infraestrutura",
        "custo": 2200,
        "manutencao": 140,
        "empregos": 4,
        "gera_agua": 18,
        "consumo_energia": 2,
        "capacidade_saude": 3,
        "beneficio_principal": "+18 de capacidade de agua",
    },
    "usina_solar": {
        "nome": "Usina solar",
        "categoria": "ambiental",
        "custo": 2400,
        "manutencao": 110,
        "empregos": 4,
        "gera_energia": 20,
        "consumo_agua": 1,
        "poluicao": -2,
        "beneficio_principal": "+20 de capacidade de energia",
    },
}

EVENTOS = [
    {"id": "seca", "titulo": "Seca", "descricao": "A falta de chuva reduziu os reservatorios da cidade.", "chance": 14, "efeitos": {"agua": -12, "saude": -2, "qualidade_vida": -3}},
    {"id": "crescimento", "titulo": "Crescimento economico", "descricao": "Novos investidores se interessaram pela cidade.", "chance": 12, "efeitos": {"dinheiro": 600, "empregos": 6, "qualidade_vida": 1}},
    {"id": "epidemia", "titulo": "Epidemia", "descricao": "Um surto aumentou a pressao sobre o sistema de saude.", "chance": 10, "efeitos": {"saude": -9, "qualidade_vida": -4, "dinheiro": -350}},
    {"id": "protestos", "titulo": "Protestos", "descricao": "Moradores reclamam da queda na qualidade de vida.", "chance": 11, "efeitos": {"qualidade_vida": -5, "dinheiro": -250}},
    {"id": "mutirao", "titulo": "Mutirao ambiental", "descricao": "A comunidade ajudou a recuperar areas verdes.", "chance": 10, "efeitos": {"poluicao": -6, "qualidade_vida": 3}},
]


def dados_construcao_nivel(tipo, nivel):
    base = CONSTRUCOES[tipo]
    config = CONFIG_UPGRADES[nivel]
    dados = {**base, "tipo": tipo, "nivel": nivel}
    beneficios = (
        "capacidade_populacional", "empregos", "gera_agua", "gera_energia",
        "capacidade_saude", "capacidade_educacao", "atividade_economica", "poluicao",
    )
    consumos = ("consumo_agua", "consumo_energia")
    for chave in beneficios:
        dados[chave] = round(base.get(chave, 0) * config["beneficio"])
    for chave in consumos:
        dados[chave] = round(base.get(chave, 0) * config["consumo"])
    dados["manutencao"] = round(base["manutencao"] * config["manutencao"])
    proximo = CONFIG_UPGRADES.get(nivel + 1)
    dados["custo_upgrade"] = round(base["custo"] * config["custo_upgrade"]) if proximo else None
    return dados
