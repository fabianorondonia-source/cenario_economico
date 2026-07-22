"""
Ranking de provedores de banda larga fixa (base de clientes) — nacional e,
quando houver fonte confiável, por UF.

Não existe endpoint aberto/sem-chave que devolva esse ranking pronto:
- dados.gov.br exige API key registrada (fora do padrão "sem cadastro" do
  projeto) — devolve 401 em toda chamada sem chave.
- O CSV bruto da Anatel (Acessos - Banda Larga Fixa, por Empresa/UF) existe
  em informacoes.anatel.gov.br, mas o nome exato do arquivo consolidado não
  foi localizado (tentativas de URL direta resultaram em 404).
Por isso este módulo é curadoria manual, igual a sector.py: número, fonte e
data ficam explícitos em cada registro, e o front-end marca "manual".

Ranking estadual (RO/MT/TO/PA/MS) por base de clientes (22/07/2026): o
Fabiano indicou a fonte — o painel oficial da Anatel
(informacoes.anatel.gov.br/paineis/acessos/ranking), aba "Banda Larga
Fixa", com filtro de UF. Não tem endpoint aberto/sem-chave (é um relatório
Power BI embarcado), então os números foram coletados navegando o painel
de verdade (Claude in Chrome) e lidos diretamente da tabela "Assinaturas de
Banda Larga Fixa por empresa - <UF> (mai-2026)" — dado oficial, mas
coletado manualmente, por isso também fica marcado "manual" como o
restante da curadoria deste projeto.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402

FONTE_NACIONAL = "Anatel, via TeleSíntese (02/02/2026) — acessos de banda larga fixa, base dez/2025"

# Ordenado pela base de clientes (mil acessos) — a métrica pedida.
RANKING_NACIONAL = [
    {"posicao": 1,  "nome": "Claro",            "acessos_mil": 10617, "market_share": 19.7},
    {"posicao": 2,  "nome": "Vivo",              "acessos_mil": 8042,  "market_share": 14.9},
    {"posicao": 3,  "nome": "Oi",                "acessos_mil": 3693,  "market_share": 6.9},
    {"posicao": 4,  "nome": "Giga Mais Fibra",   "acessos_mil": 1580,  "market_share": 2.7},
    {"posicao": 5,  "nome": "Brisanet",          "acessos_mil": 1554,  "market_share": 2.9},
    {"posicao": 6,  "nome": "Vero",              "acessos_mil": 1355,  "market_share": 2.5},
    {"posicao": 7,  "nome": "Brasil Tecpar",     "acessos_mil": 1344,  "market_share": 2.5},
    {"posicao": 8,  "nome": "Desktop",           "acessos_mil": 1207,  "market_share": 2.2},
    {"posicao": 9,  "nome": "TIM",               "acessos_mil": 856,   "market_share": 1.6},
    {"posicao": 10, "nome": "Unifique",          "acessos_mil": 843,   "market_share": 1.6},
]


FONTE_ESTADUAL = "Anatel — Painel de Acessos (informacoes.anatel.gov.br/paineis/acessos/ranking), Banda Larga Fixa por UF (mai-2026)"

RANKING_RO = [
    {"posicao": 1,  "nome": "Uni Telecom",        "acessos": 122502, "market_share": 24.0},
    {"posicao": 2,  "nome": "Oi",                  "acessos": 79602,  "market_share": 15.6},
    {"posicao": 3,  "nome": "Claro",               "acessos": 42108,  "market_share": 8.2},
    {"posicao": 4,  "nome": "Rolim Net",           "acessos": 31087,  "market_share": 6.1},
    {"posicao": 5,  "nome": "Brasil Digital Telecom", "acessos": 27783, "market_share": 5.4},
    {"posicao": 6,  "nome": "Speed Travel",        "acessos": 15565,  "market_share": 3.0},
    {"posicao": 7,  "nome": "Olla Servicos & Internet", "acessos": 13101, "market_share": 2.6},
    {"posicao": 8,  "nome": "Starlink Brazil",     "acessos": 12677,  "market_share": 2.5},
    {"posicao": 9,  "nome": "Worldnet Fibra Optica", "acessos": 11646, "market_share": 2.3},
    {"posicao": 10, "nome": "Net Way Informatica", "acessos": 11353,  "market_share": 2.2},
]

RANKING_MT = [
    {"posicao": 1,  "nome": "Brasil Tecpar",       "acessos": 229180, "market_share": 23.1},
    {"posicao": 2,  "nome": "Claro",               "acessos": 110040, "market_share": 11.1},
    {"posicao": 3,  "nome": "Vivo",                "acessos": 76031,  "market_share": 7.7},
    {"posicao": 4,  "nome": "Oi",                  "acessos": 74484,  "market_share": 7.5},
    {"posicao": 5,  "nome": "Starlink Brazil",     "acessos": 66644,  "market_share": 6.7},
    {"posicao": 6,  "nome": "Nave Net",            "acessos": 51313,  "market_share": 5.2},
    {"posicao": 7,  "nome": "Gb Online",           "acessos": 47665,  "market_share": 4.8},
    {"posicao": 8,  "nome": "Interfibras",         "acessos": 29513,  "market_share": 3.0},
    {"posicao": 9,  "nome": "Quick Telecomunicacoes", "acessos": 19079, "market_share": 1.9},
    {"posicao": 10, "nome": "Lci Telecom",         "acessos": 18942,  "market_share": 1.9},
]

RANKING_TO = [
    {"posicao": 1,  "nome": "Pronto Fibra",        "acessos": 42739,  "market_share": 15.7},
    {"posicao": 2,  "nome": "Aranet Solucoes",     "acessos": 32886,  "market_share": 12.1},
    {"posicao": 3,  "nome": "Claro",               "acessos": 30371,  "market_share": 11.2},
    {"posicao": 4,  "nome": "Oi",                  "acessos": 30340,  "market_share": 11.2},
    {"posicao": 5,  "nome": "Starlink Brazil",     "acessos": 25504,  "market_share": 9.4},
    {"posicao": 6,  "nome": "Conectlan",           "acessos": 14058,  "market_share": 5.2},
    {"posicao": 7,  "nome": "Vivo",                "acessos": 10496,  "market_share": 3.9},
    {"posicao": 8,  "nome": "Netbox",              "acessos": 10095,  "market_share": 3.7},
    {"posicao": 9,  "nome": "Info-Tel",            "acessos": 10016,  "market_share": 3.7},
    {"posicao": 10, "nome": "Cdi Net",             "acessos": 5559,   "market_share": 2.0},
]

RANKING_PA = [
    {"posicao": 1,  "nome": "Claro",               "acessos": 147952, "market_share": 12.3},
    {"posicao": 2,  "nome": "Oi",                  "acessos": 131613, "market_share": 11.0},
    {"posicao": 3,  "nome": "Starlink Brazil",     "acessos": 103768, "market_share": 8.7},
    {"posicao": 4,  "nome": "Vivo",                "acessos": 85302,  "market_share": 7.1},
    {"posicao": 5,  "nome": "Sea Telecom",         "acessos": 67732,  "market_share": 5.6},
    {"posicao": 6,  "nome": "Fibralink",           "acessos": 61064,  "market_share": 5.1},
    {"posicao": 7,  "nome": "Voce Telecom",        "acessos": 47441,  "market_share": 4.0},
    {"posicao": 8,  "nome": "Online Norte",        "acessos": 46106,  "market_share": 3.8},
    {"posicao": 9,  "nome": "Jupiter Internet Imperatriz", "acessos": 38941, "market_share": 3.2},
    {"posicao": 10, "nome": "Wlan Sistemas de Telecom.", "acessos": 30677, "market_share": 2.6},
]

RANKING_MS = [
    {"posicao": 1,  "nome": "Claro",               "acessos": 116376, "market_share": 16.0},
    {"posicao": 2,  "nome": "Digital Net",         "acessos": 84869,  "market_share": 11.7},
    {"posicao": 3,  "nome": "Oi",                  "acessos": 80568,  "market_share": 11.1},
    {"posicao": 4,  "nome": "Vivo",                "acessos": 72747,  "market_share": 10.0},
    {"posicao": 5,  "nome": "Opcao Telecom",       "acessos": 49444,  "market_share": 6.8},
    {"posicao": 6,  "nome": "Giga Mais Fibra",     "acessos": 37024,  "market_share": 5.1},
    {"posicao": 7,  "nome": "Vero",                "acessos": 35135,  "market_share": 4.8},
    {"posicao": 8,  "nome": "Starlink Brazil",     "acessos": 28682,  "market_share": 3.9},
    {"posicao": 9,  "nome": "Hokinet",             "acessos": 19012,  "market_share": 2.6},
    {"posicao": 10, "nome": "Brasil Tecpar",       "acessos": 17334,  "market_share": 2.4},
]

RANKINGS_ESTADUAIS = {
    "ranking_ro": ("RO", RANKING_RO),
    "ranking_mt": ("MT", RANKING_MT),
    "ranking_to": ("TO", RANKING_TO),
    "ranking_pa": ("PA", RANKING_PA),
    "ranking_ms": ("MS", RANKING_MS),
}


def atualizar_todos():
    db.upsert_indicador(
        chave="ranking_nacional", categoria="telecom_ranking", valor=None, unidade="lista",
        fonte=FONTE_NACIONAL, atualizacao="manual", historico=RANKING_NACIONAL
    )
    print("[telecom.ranking] ranking nacional de provedores carregado no cache.")

    for chave, (uf, ranking) in RANKINGS_ESTADUAIS.items():
        db.upsert_indicador(
            chave=chave, categoria="telecom_ranking", valor=None, unidade="lista",
            fonte=FONTE_ESTADUAL, atualizacao="manual", historico=ranking
        )
        print(f"[telecom.ranking] ranking de {uf} carregado no cache.")


if __name__ == "__main__":
    atualizar_todos()
