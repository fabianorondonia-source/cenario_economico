"""
Ranking de provedores de banda larga fixa (base de clientes) — nacional e
por UF (RO/MT/TO/PA/MS, área de atuação do Grupo Netway).

Fonte oficial: painel público da Anatel
(informacoes.anatel.gov.br/paineis/acessos/ranking), aba "Banda Larga
Fixa", com filtro de UF. É um relatório Power BI embarcado — não existe
endpoint aberto/sem-chave pra consultar isso via API (dados.gov.br devolve
401 sem chave registrada; o CSV bruto da Anatel não tem nome de arquivo
localizável). Por isso os números foram coletados navegando o painel de
verdade (Claude in Chrome) e lidos direto da tabela "Assinaturas de Banda
Larga Fixa por empresa" (nacional e cada UF), com o visual expandido em
tela cheia pra evitar truncamento de número grande. Curadoria manual, igual
a sector.py: fonte e período ficam explícitos, front-end marca "manual".

PERÍODO DE REFERÊNCIA: a Anatel publica com defasagem de ~1-2 meses — em
22/07/2026 o mês mais recente disponível no painel era **mai-2026** (não
existe jun/jul-2026 ainda; confirmado no seletor "Período" do próprio
painel, que lista mai-2026 como opção mais recente). Atualizar este
período requer voltar ao painel e checar se um mês novo apareceu no
seletor antes de recoletar — não presumir que "mês mais recente do
calendário" = "mês disponível na Anatel".
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402

PERIODO_REFERENCIA = "mai-2026"
FONTE_NACIONAL = f"Anatel — Painel de Acessos (informacoes.anatel.gov.br/paineis/acessos/ranking), Banda Larga Fixa Brasil ({PERIODO_REFERENCIA})"

# Ordenado pela base de clientes (acessos). Mesma fonte/período dos rankings
# estaduais abaixo (substituiu uma curadoria anterior via TeleSíntese/dez-2025,
# que era menos atual e de fonte diferente).
RANKING_NACIONAL = [
    {"posicao": 1,  "nome": "Claro",            "acessos": 10784341, "market_share": 19.5},
    {"posicao": 2,  "nome": "Vivo",              "acessos": 8352443,  "market_share": 15.1},
    {"posicao": 3,  "nome": "Oi",                "acessos": 3458749,  "market_share": 6.2},
    {"posicao": 4,  "nome": "Brisanet",          "acessos": 1578364,  "market_share": 2.8},
    {"posicao": 5,  "nome": "Brasil Tecpar",     "acessos": 1370170,  "market_share": 2.5},
    {"posicao": 6,  "nome": "Giga Mais Fibra",   "acessos": 1329846,  "market_share": 2.4},
    {"posicao": 7,  "nome": "Vero",              "acessos": 1311590,  "market_share": 2.4},
    {"posicao": 8,  "nome": "Desktop",           "acessos": 1200501,  "market_share": 2.2},
    {"posicao": 9,  "nome": "TIM",               "acessos": 901550,   "market_share": 1.6},
    {"posicao": 10, "nome": "Unifique",          "acessos": 883910,   "market_share": 1.6},
]


FONTE_ESTADUAL = f"Anatel — Painel de Acessos (informacoes.anatel.gov.br/paineis/acessos/ranking), Banda Larga Fixa por UF ({PERIODO_REFERENCIA})"

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


def _classificar_hhi(hhi):
    # Faixas do DOJ/FTC (usadas também como referência no Brasil por Cade/
    # Anatel em análises de concentração): <1500 pouco concentrado,
    # 1500-2500 moderadamente concentrado, >2500 altamente concentrado.
    if hhi >= 2500:
        return "alta concentração"
    if hhi >= 1500:
        return "concentração moderada"
    return "baixa concentração (fragmentado)"


def calcular_hhi_por_uf():
    """HHI (Herfindahl-Hirschman) calculado só com o TOP 10 informado pela
    Anatel por UF — não é o HHI real do mercado (faltam os pequenos
    provedores da "cauda longa", que reduziriam ainda mais o HHI real do
    top 10 sozinho já é subestimado por natureza, mas é honesto e serve
    muito bem pra COMPARAR concentração relativa entre os 5 estados de
    atuação da Netway, que é o uso pretendido aqui: menor HHI = mercado
    mais fragmentado (mais alvos de roll-up, nenhum dono claro); maior HHI
    = já existe um líder consolidado (RO, por causa da Uni Telecom com 24%
    sozinha) — devir a due diligence prioritária pra ESSE ativo específico,
    não pro mercado como um todo.
    """
    resultado = []
    for chave, (uf, ranking) in RANKINGS_ESTADUAIS.items():
        hhi = sum((p["market_share"]) ** 2 for p in ranking)
        lider = max(ranking, key=lambda p: p["market_share"])
        resultado.append({
            "uf": uf,
            "hhi_top10": round(hhi, 0),
            "nivel": _classificar_hhi(hhi),
            "lider": lider["nome"],
            "lider_share": lider["market_share"],
        })
    return resultado


def calcular_ameaca_starlink():
    """Starlink já aparece nos rankings estaduais coletados — em vez de
    deixar isso só como mais uma linha na tabela, extrai a posição/share
    dele em cada UF e classifica o nível de ameaça. É a ameaça competitiva
    mais relevante especificamente pra área RURAL onde a Netway atua (não
    depende de concorrente construir rede física local), por isso merece
    destaque próprio em vez de ficar escondido em 5 tabelas diferentes.
    """
    resultado = []
    for chave, (uf, ranking) in RANKINGS_ESTADUAIS.items():
        starlink = next((p for p in ranking if "Starlink" in p["nome"]), None)
        if not starlink:
            resultado.append({"uf": uf, "presente": False, "nivel": "fora do top 10"})
            continue
        share = starlink["market_share"]
        if share >= 8:
            nivel = "ameaça alta"
        elif share >= 4:
            nivel = "ameaça moderada"
        else:
            nivel = "ameaça baixa"
        resultado.append({
            "uf": uf, "presente": True, "posicao": starlink["posicao"],
            "market_share": share, "nivel": nivel,
        })
    return resultado


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

    hhi = calcular_hhi_por_uf()
    db.upsert_indicador(
        chave="hhi_estados", categoria="telecom_ranking", valor=None, unidade="HHI (top 10)",
        fonte=f"Calculado a partir dos rankings Anatel acima ({PERIODO_REFERENCIA})",
        atualizacao="manual", historico=hhi
    )
    print("[telecom.ranking] HHI de concentração por estado calculado.")

    ameaca_starlink = calcular_ameaca_starlink()
    db.upsert_indicador(
        chave="ameaca_starlink", categoria="telecom_ranking", valor=None, unidade="nível",
        fonte=f"Calculado a partir dos rankings Anatel acima ({PERIODO_REFERENCIA})",
        atualizacao="manual", historico=ameaca_starlink
    )
    print("[telecom.ranking] ameaça Starlink por estado calculada.")


if __name__ == "__main__":
    atualizar_todos()
