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
01/08/2026 o mês mais recente disponível no painel era **jun-2026** (não
existe jul-2026 ainda; confirmado no seletor "Período" do próprio
painel, que lista jun-2026 como opção mais recente). Atualizar este
período requer voltar ao painel e checar se um mês novo apareceu no
seletor antes de recoletar — não presumir que "mês mais recente do
calendário" = "mês disponível na Anatel".
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402

PERIODO_REFERENCIA = "jun-2026"
FONTE_NACIONAL = f"Anatel — Painel de Acessos (informacoes.anatel.gov.br/paineis/acessos/ranking), Banda Larga Fixa Brasil ({PERIODO_REFERENCIA})"

# Ordenado pela base de clientes (acessos). Mesma fonte/período dos rankings
# estaduais abaixo (substituiu uma curadoria anterior via TeleSíntese/dez-2025,
# que era menos atual e de fonte diferente).
RANKING_NACIONAL = [
    {"posicao": 1,  "nome": "Claro",            "acessos": 10805062, "market_share": 19.1},
    {"posicao": 2,  "nome": "Vivo",              "acessos": 8409356,  "market_share": 14.9},
    {"posicao": 3,  "nome": "Oi",                "acessos": 3434931,  "market_share": 6.1},
    {"posicao": 4,  "nome": "Brisanet",          "acessos": 1579840,  "market_share": 2.8},
    {"posicao": 5,  "nome": "Brasil Tecpar",     "acessos": 1372924,  "market_share": 2.4},
    {"posicao": 6,  "nome": "Giga Mais Fibra",   "acessos": 1313370,  "market_share": 2.3},
    {"posicao": 7,  "nome": "Vero",              "acessos": 1305248,  "market_share": 2.3},
    {"posicao": 8,  "nome": "Desktop",           "acessos": 1199770,  "market_share": 2.1},
    {"posicao": 9,  "nome": "TIM",               "acessos": 906476,   "market_share": 1.6},
    {"posicao": 10, "nome": "Unifique",          "acessos": 885395,   "market_share": 1.6},
]


FONTE_ESTADUAL = f"Anatel — Painel de Acessos (informacoes.anatel.gov.br/paineis/acessos/ranking), Banda Larga Fixa por UF ({PERIODO_REFERENCIA})"

RANKING_RO = [
    {"posicao": 1,  "nome": "Uni Telecom",        "acessos": 132227, "market_share": 25.6},
    {"posicao": 2,  "nome": "Oi",                  "acessos": 78922,  "market_share": 15.3},
    {"posicao": 3,  "nome": "Claro",               "acessos": 42601,  "market_share": 8.3},
    {"posicao": 4,  "nome": "Rolim Net",           "acessos": 31087,  "market_share": 6.0},
    {"posicao": 5,  "nome": "Brasil Digital Telecom", "acessos": 28028, "market_share": 5.4},
    {"posicao": 6,  "nome": "Speed Travel",        "acessos": 15777,  "market_share": 3.1},
    {"posicao": 7,  "nome": "Starlink Brazil",     "acessos": 13463,  "market_share": 2.6},
    {"posicao": 8,  "nome": "Olla Servicos & Internet", "acessos": 12556, "market_share": 2.4},
    {"posicao": 9,  "nome": "Worldnet Fibra Optica", "acessos": 11790, "market_share": 2.3},
    {"posicao": 10, "nome": "Net Way Informatica", "acessos": 10901,  "market_share": 2.1},
]

RANKING_MT = [
    {"posicao": 1,  "nome": "Brasil Tecpar",       "acessos": 229399, "market_share": 24.4},
    {"posicao": 2,  "nome": "Claro",               "acessos": 110374, "market_share": 11.7},
    {"posicao": 3,  "nome": "Vivo",                "acessos": 76390,  "market_share": 8.1},
    {"posicao": 4,  "nome": "Oi",                  "acessos": 73441,  "market_share": 7.8},
    {"posicao": 5,  "nome": "Starlink Brazil",     "acessos": 69992,  "market_share": 7.4},
    {"posicao": 6,  "nome": "Gb Online",           "acessos": 47788,  "market_share": 5.1},
    {"posicao": 7,  "nome": "Nave Net",            "acessos": 44426,  "market_share": 4.7},
    {"posicao": 8,  "nome": "Quick Telecomunicacoes", "acessos": 19079, "market_share": 2.0},
    {"posicao": 9,  "nome": "Lci Telecom",         "acessos": 18957,  "market_share": 2.0},
    {"posicao": 10, "nome": "Rv - Net",            "acessos": 18944,  "market_share": 2.0},
]

RANKING_TO = [
    {"posicao": 1,  "nome": "Pronto Fibra",        "acessos": 43380,  "market_share": 13.7},
    {"posicao": 2,  "nome": "Aranet Solucoes",     "acessos": 33235,  "market_share": 10.5},
    {"posicao": 3,  "nome": "Oi",                  "acessos": 30430,  "market_share": 9.6},
    {"posicao": 4,  "nome": "Claro",               "acessos": 30425,  "market_share": 9.6},
    {"posicao": 5,  "nome": "Toledo Fibra",        "acessos": 27571,  "market_share": 8.7},
    {"posicao": 6,  "nome": "Starlink Brazil",     "acessos": 27242,  "market_share": 8.6},
    {"posicao": 7,  "nome": "Lucaroni Telecom",    "acessos": 14450,  "market_share": 4.6},
    {"posicao": 8,  "nome": "Conectlan",           "acessos": 13943,  "market_share": 4.4},
    {"posicao": 9,  "nome": "Vivo",                "acessos": 10468,  "market_share": 3.3},
    {"posicao": 10, "nome": "Netbox",              "acessos": 10273,  "market_share": 3.3},
]

RANKING_PA = [
    {"posicao": 1,  "nome": "Claro",               "acessos": 148185, "market_share": 12.1},
    {"posicao": 2,  "nome": "Oi",                  "acessos": 132295, "market_share": 10.8},
    {"posicao": 3,  "nome": "Starlink Brazil",     "acessos": 109887, "market_share": 9.0},
    {"posicao": 4,  "nome": "Vivo",                "acessos": 85559,  "market_share": 7.0},
    {"posicao": 5,  "nome": "Sea Telecom",         "acessos": 67352,  "market_share": 5.5},
    {"posicao": 6,  "nome": "Fibralink",           "acessos": 61403,  "market_share": 5.0},
    {"posicao": 7,  "nome": "Voce Telecom",        "acessos": 56700,  "market_share": 4.6},
    {"posicao": 8,  "nome": "Online Norte",        "acessos": 45828,  "market_share": 3.7},
    {"posicao": 9,  "nome": "Jupiter Internet Imperatriz", "acessos": 38699, "market_share": 3.2},
    {"posicao": 10, "nome": "Wlan Sistemas de Telecom.", "acessos": 30677, "market_share": 2.5},
]

RANKING_MS = [
    {"posicao": 1,  "nome": "Opcao Telecom",       "acessos": 146424, "market_share": 17.7},
    {"posicao": 2,  "nome": "Claro",               "acessos": 116966, "market_share": 14.1},
    {"posicao": 3,  "nome": "Digital Net",         "acessos": 84154,  "market_share": 10.1},
    {"posicao": 4,  "nome": "Oi",                  "acessos": 78852,  "market_share": 9.5},
    {"posicao": 5,  "nome": "Vivo",                "acessos": 73569,  "market_share": 8.9},
    {"posicao": 6,  "nome": "Giga Mais Fibra",     "acessos": 36246,  "market_share": 4.4},
    {"posicao": 7,  "nome": "Vero",                "acessos": 34854,  "market_share": 4.2},
    {"posicao": 8,  "nome": "Starlink Brazil",     "acessos": 30177,  "market_share": 3.6},
    {"posicao": 9,  "nome": "Hokinet",             "acessos": 19132,  "market_share": 2.3},
    {"posicao": 10, "nome": "Brasil Tecpar",       "acessos": 17436,  "market_share": 2.1},
]

RANKINGS_ESTADUAIS = {
    "ranking_ro": ("RO", RANKING_RO),
    "ranking_mt": ("MT", RANKING_MT),
    "ranking_to": ("TO", RANKING_TO),
    "ranking_pa": ("PA", RANKING_PA),
    "ranking_ms": ("MS", RANKING_MS),
}


# Evolução mês a mês da base de clientes em RO (jan-2026 até o período de
# referência acima) — pedido explícito do Fabiano pra enxergar o CRESCIMENTO
# de cada operadora ao longo do ano, não só o snapshot do mês mais recente.
# Coletado navegando o mesmo painel Anatel, trocando o filtro "Período" mês a
# mês (RO fixo). Cobre as 5 operadoras mais relevantes do top 10 pra manter o
# gráfico de linhas legível — a mudança mais importante que aparece aqui é a
# Uni Telecom saindo de 2º lugar (62 mil, jan) pra 1º isolado (132 mil, jun),
# ultrapassando a Oi em março e mais que dobrando de base em 6 meses,
# enquanto a Oi ficou praticamente estável/levemente em queda.
EVOLUCAO_RO_MENSAL = {
    "periodos": ["jan-2026", "fev-2026", "mar-2026", "abr-2026", "mai-2026", "jun-2026"],
    "series": [
        {"nome": "Uni Telecom",            "acessos": [62196, 58368, 87486, 122502, 122502, 132227]},
        {"nome": "Oi",                      "acessos": [81088, 80581, 80071, 80378, 79602, 78922]},
        {"nome": "Claro",                   "acessos": [40412, 40950, 41421, 41801, 42108, 42601]},
        {"nome": "Rolim Net",               "acessos": [27235, 28246, 29019, 29308, 31087, 31087]},
        {"nome": "Brasil Digital Telecom",  "acessos": [30601, 25416, 29476, 29368, 27783, 28028]},
    ],
}
FONTE_EVOLUCAO_RO = "Anatel — Painel de Acessos (informacoes.anatel.gov.br/paineis/acessos/ranking), Banda Larga Fixa RO, coletado mês a mês (jan-2026 a jun-2026, alterando o filtro Período)"


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

    db.upsert_indicador(
        chave="evolucao_ro_mensal", categoria="telecom_ranking", valor=None, unidade="acessos por mês",
        fonte=FONTE_EVOLUCAO_RO, atualizacao="manual", historico=EVOLUCAO_RO_MENSAL
    )
    print("[telecom.ranking] evolução mensal de RO (jan-jun/2026) carregada no cache.")


if __name__ == "__main__":
    atualizar_todos()
