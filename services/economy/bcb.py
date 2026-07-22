"""
Fonte de dados: Banco Central do Brasil — SGS (Sistema Gerenciador de Séries
Temporais). API pública, gratuita, sem necessidade de cadastro/chave:
  https://api.bcb.gov.br/dados/serie/bcdata.sgs.<codigo>/dados/ultimos/<N>?formato=json

Cobre: economia (PIB, IPCA, IGP-M, Selic, desemprego, dívida pública,
resultado fiscal, produção industrial, varejo) e crédito (spread bancário,
taxa média de juros, inadimplência). Cada série é buscada de forma
independente — se uma falhar, as outras continuam normalmente.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402
from services._http import abrir_url, descrever_erro  # noqa: E402

TIMEOUT = 10
MAX_HISTORICO = 120

# Registro de séries do SGS usadas no painel. Códigos conferidos contra a
# documentação pública do SGS; se algum código estiver desatualizado, o
# fetch falha de forma isolada (log no console) e o valor anterior em cache
# é mantido — não derruba o restante da atualização.
SERIES_ECONOMIA = {
    "selic_meta":        {"codigo": 432,   "unidade": "% a.a.",   "categoria": "economia", "label": "Selic (meta)"},
    "ipca_mensal":       {"codigo": 433,   "unidade": "%",        "categoria": "economia", "label": "IPCA (mensal)"},
    "igpm_mensal":       {"codigo": 189,   "unidade": "%",        "categoria": "economia", "label": "IGP-M (mensal)"},
    "dolar_ptax":        {"codigo": 1,     "unidade": "R$",       "categoria": "mercado",  "label": "Dólar (PTAX venda)"},
    "euro_ptax":         {"codigo": 21619, "unidade": "R$",       "categoria": "mercado",  "label": "Euro (PTAX venda)"},
    "desemprego":        {"codigo": 24369, "unidade": "%",        "categoria": "economia", "label": "Taxa de desocupação"},
    "divida_bruta_pib":  {"codigo": 13762, "unidade": "% PIB",    "categoria": "economia", "label": "Dívida Bruta do Governo Geral"},
    "resultado_primario":{"codigo": 5793,  "unidade": "R$ milhões","categoria": "economia","label": "Resultado primário do governo central"},
    "producao_industrial":{"codigo": 21859,"unidade": "índice",   "categoria": "economia", "label": "Produção industrial"},
    "vendas_varejo":     {"codigo": 1455,  "unidade": "índice",   "categoria": "economia", "label": "Vendas no varejo"},
    "spread_bancario":   {"codigo": 20783, "unidade": "p.p.",     "categoria": "credito",  "label": "Spread bancário médio"},
    "taxa_media_credito":{"codigo": 20714, "unidade": "% a.a.",   "categoria": "credito",  "label": "Taxa média de juros do crédito"},
    "inadimplencia":     {"codigo": 21082, "unidade": "%",        "categoria": "credito",  "label": "Inadimplência (recursos livres)"},
}


def log(msg):
    print(f"[bcb] {msg}")


def _http_get_json(url):
    with abrir_url(url, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _data_iso(data_br):
    """BCB devolve datas em DD/MM/YYYY. Convertido pra YYYY-MM-DD (ISO) pra o
    Plotly no front-end conseguir tratar o eixo como data de verdade —
    string DD/MM/YYYY ordenada como texto vira zigue-zague errado assim que
    a série cruza um mês (ex.: "01/02" ordena antes de "15/01")."""
    try:
        d, m, a = data_br.split("/")
        return f"{a}-{m}-{d}"
    except (ValueError, AttributeError):
        return data_br


def buscar_serie(codigo_sgs, n_dias=MAX_HISTORICO):
    """Busca os últimos N dias de uma série do SGS. O endpoint 'ultimos/N'
    do BCB passou a devolver 400 Bad Request para N grande (confirmado em
    testes: N=120/100/50/30/25 falham, N=20 funciona) — não é falta de
    internet nem bloqueio, é o próprio parâmetro sendo rejeitado. Em vez de
    depender de um número mágico que pode mudar de novo, tenta uma escada de
    janelas menores até uma responder, começando pela pedida."""
    candidatos = sorted({n_dias, 90, 60, 30, 20, 10}, reverse=True)
    candidatos = [n for n in candidatos if n <= n_dias] or [10]
    ultimo_erro = None
    for n in candidatos:
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_sgs}/dados/ultimos/{n}?formato=json"
        try:
            serie = _http_get_json(url)
            return [{"data": _data_iso(p["data"]), "valor": float(p["valor"].replace(",", "."))} for p in serie]
        except Exception as e:
            ultimo_erro = e
            continue
    raise ultimo_erro


def calcular_ipca_12m():
    """IPCA acumulado 12 meses = produtório dos últimos 12 valores mensais (%)."""
    serie = buscar_serie(433, n_dias=12)
    if len(serie) < 12:
        return None
    acumulado = 1.0
    for p in serie:
        acumulado *= (1 + p["valor"] / 100)
    return {"valor": round((acumulado - 1) * 100, 2), "data": serie[-1]["data"]}


def atualizar_todos():
    """Busca todas as séries do registro e grava no cache SQLite."""
    for chave, meta in SERIES_ECONOMIA.items():
        try:
            historico = buscar_serie(meta["codigo"])
            if not historico:
                log(f"{chave}: série vazia, mantendo cache anterior.")
                continue
            atual = historico[-1]
            anterior = historico[-2] if len(historico) > 1 else None
            variacao = None
            if anterior and anterior["valor"]:
                variacao = round(((atual["valor"] - anterior["valor"]) / anterior["valor"]) * 100, 2)
            db.upsert_indicador(
                chave=chave, categoria=meta["categoria"], valor=atual["valor"],
                unidade=meta["unidade"], data_referencia=atual["data"],
                variacao_dia=variacao, fonte=f"Banco Central — SGS {meta['codigo']}",
                atualizacao="automatica", historico=historico
            )
            log(f"{chave}: {atual['valor']} ({atual['data']}) — OK")
        except Exception as e:
            log(f"{chave}: falhou ({descrever_erro(e)}). Mantendo cache anterior.")

    # IPCA acumulado 12 meses (calculado, não é uma série SGS única)
    try:
        r = calcular_ipca_12m()
        if r:
            db.upsert_indicador(
                chave="ipca_12m", categoria="economia", valor=r["valor"], unidade="%",
                data_referencia=r["data"], fonte="Calculado a partir da SGS 433 (acumulado 12 meses)",
                atualizacao="automatica"
            )
            log(f"ipca_12m: {r['valor']}% — OK")
    except Exception as e:
        log(f"ipca_12m: falhou ({descrever_erro(e)}).")


if __name__ == "__main__":
    atualizar_todos()
