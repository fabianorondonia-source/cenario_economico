"""
Mercado financeiro — fontes 100% gratuitas e sem necessidade de cadastro/chave:

  - stooq.com — CSV histórico diário (https://stooq.com/q/d/l/?s=<symbol>&i=d),
    usado para índices e commodities: Ibovespa, S&P 500, Nasdaq, Dow Jones,
    ouro, petróleo, VIX (volatilidade).
  - CoinGecko — API pública (https://api.coingecko.com/api/v3/...) para Bitcoin.

Símbolos de índice variam entre provedores e de vez em quando mudam — cada
indicador tem uma lista de símbolos candidatos, tentados em ordem; o primeiro
que responder com dado válido é usado. Se nenhum responder, o valor anterior
em cache é mantido (nunca quebra a atualização como um todo).
"""

import csv
import io
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402
from services._http import abrir_url, descrever_erro  # noqa: E402

TIMEOUT = 10
MAX_HISTORICO = 120

# chave -> (lista de símbolos stooq candidatos, label, unidade)
INDICES_STOOQ = {
    "ibovespa":  {"simbolos": ["^bvsp", "bvsp"],           "unidade": "pontos", "label": "Ibovespa"},
    "sp500":     {"simbolos": ["^spx"],                     "unidade": "pontos", "label": "S&P 500"},
    "nasdaq":    {"simbolos": ["^ndq", "^ixic"],            "unidade": "pontos", "label": "Nasdaq Composite"},
    "dow_jones": {"simbolos": ["^dji"],                     "unidade": "pontos", "label": "Dow Jones"},
    "ouro":      {"simbolos": ["xauusd"],                   "unidade": "US$/oz", "label": "Ouro (XAU/USD)"},
    "petroleo":  {"simbolos": ["cl.f"],                     "unidade": "US$/barril", "label": "Petróleo (WTI)"},
    "vix":       {"simbolos": ["^vix"],                     "unidade": "pontos", "label": "Volatilidade (VIX)"},
}


def log(msg):
    print(f"[markets] {msg}")


def _stooq_csv(simbolo):
    url = f"https://stooq.com/q/d/l/?s={simbolo}&i=d"
    with abrir_url(url, timeout=TIMEOUT) as resp:
        texto = resp.read().decode("utf-8", errors="replace")
    linhas = list(csv.DictReader(io.StringIO(texto)))
    if not linhas or "Date" not in (linhas[0] or {}):
        # stooq às vezes devolve "Exceeded the daily hits limit" ou uma
        # página de bloqueio em vez do CSV — loga um trecho pra facilitar
        # diagnóstico em vez de só dizer "vazio".
        amostra = texto.strip().replace("\n", " ")[:120]
        log(f"{simbolo}: resposta não é CSV válido — trecho: {amostra!r}")
        return []
    out = []
    for row in linhas:
        try:
            out.append({"data": row["Date"], "valor": float(row["Close"])})
        except (ValueError, KeyError, TypeError):
            continue
    return out


def _buscar_indice(simbolos, n_dias=MAX_HISTORICO):
    ultimo_erro = None
    for s in simbolos:
        try:
            historico = _stooq_csv(s)
            if historico:
                return historico[-n_dias:]
        except Exception as e:
            ultimo_erro = e
            continue
    if ultimo_erro:
        log(f"nenhum símbolo respondeu ({simbolos}) — último erro: {descrever_erro(ultimo_erro)}")
    return []


def atualizar_indices_stooq():
    for chave, meta in INDICES_STOOQ.items():
        try:
            historico = _buscar_indice(meta["simbolos"])
            if not historico:
                log(f"{chave}: nenhum símbolo respondeu, mantendo cache anterior.")
                continue
            atual = historico[-1]
            anterior = historico[-2] if len(historico) > 1 else None
            variacao = None
            if anterior and anterior["valor"]:
                variacao = round(((atual["valor"] - anterior["valor"]) / anterior["valor"]) * 100, 2)
            db.upsert_indicador(
                chave=chave, categoria="mercado", valor=atual["valor"], unidade=meta["unidade"],
                data_referencia=atual["data"], variacao_dia=variacao, fonte="stooq.com",
                atualizacao="automatica", historico=historico
            )
            log(f"{chave}: {atual['valor']} ({atual['data']}) — OK")
        except Exception as e:
            log(f"{chave}: falhou ({descrever_erro(e)}). Mantendo cache anterior.")


def atualizar_bitcoin():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,brl&include_24hr_change=true"
        with abrir_url(url, timeout=TIMEOUT) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        btc = payload.get("bitcoin", {})
        if not btc:
            log("bitcoin: resposta vazia da CoinGecko, mantendo cache anterior.")
            return
        db.upsert_indicador(
            chave="bitcoin", categoria="mercado", valor=btc.get("usd"), unidade="US$",
            data_referencia=None, variacao_dia=btc.get("usd_24h_change"),
            fonte="CoinGecko", atualizacao="automatica"
        )
        db.upsert_indicador(
            chave="bitcoin_brl", categoria="mercado", valor=btc.get("brl"), unidade="R$",
            data_referencia=None, fonte="CoinGecko", atualizacao="automatica"
        )
        log(f"bitcoin: US$ {btc.get('usd')} — OK")
    except Exception as e:
        log(f"bitcoin: falhou ({descrever_erro(e)}). Mantendo cache anterior.")


def atualizar_todos():
    atualizar_indices_stooq()
    atualizar_bitcoin()


if __name__ == "__main__":
    atualizar_todos()
