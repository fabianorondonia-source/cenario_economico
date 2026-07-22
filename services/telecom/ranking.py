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

Ranking estadual (RO/MT/TO/PA/MS) por base de clientes: NÃO incluído aqui de
propósito. Não há fonte pública confiável de base de assinantes por operador
e por UF (apenas prêmios de satisfação/velocidade, que são outra métrica) —
o Fabiano optou por indicar a fonte quando tiver em mãos, em vez de usar
dado fabricado ou um "prêmio" como substituto. Assim que ele indicar a fonte,
adicionar aqui um dict por UF seguindo o mesmo formato de RANKING_NACIONAL.
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


def atualizar_todos():
    db.upsert_indicador(
        chave="ranking_nacional", categoria="telecom_ranking", valor=None, unidade="lista",
        fonte=FONTE_NACIONAL, atualizacao="manual", historico=RANKING_NACIONAL
    )
    print("[telecom.ranking] ranking nacional de provedores carregado no cache.")
    # Rankings estaduais (RO, MT, TO, PA, MS): aguardando fonte confiável de
    # base de assinantes por operador/UF, a ser indicada pelo Fabiano.


if __name__ == "__main__":
    atualizar_todos()
