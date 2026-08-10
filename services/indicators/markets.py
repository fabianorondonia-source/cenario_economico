"""
Mercado financeiro — fontes gratuitas e sem necessidade de cadastro/chave:

  - Yahoo Finance (query1.finance.yahoo.com/v8/finance/chart/<symbol>) — JSON
    público, sem chave, usado para índices e commodities: Ibovespa, S&P 500,
    Nasdaq, Dow Jones, ouro, petróleo, VIX (volatilidade) e as ações dos
    grupos de capital aberto do setor.
  - CoinGecko — API pública (https://api.coingecko.com/api/v3/...) para Bitcoin.

Por que não stooq.com (usado numa versão anterior): confirmado em produção
(rodando no GitHub Actions) que stooq devolve uma página de bloqueio
anti-robô (challenge com <noscript>) pro CSV histórico quando a requisição
vem de IP de nuvem/datacenter — não é algo que dá pra contornar só trocando
o User-Agent, exigiria executar JavaScript de verdade (navegador). O Yahoo
Finance tolera bem esse tipo de acesso programático.

Símbolos de índice variam entre provedores e de vez em quando mudam — cada
indicador tem uma lista de símbolos candidatos, tentados em ordem; o primeiro
que responder com dado válido é usado. Se nenhum responder, o valor anterior
em cache é mantido (nunca quebra a atualização como um todo).
"""

import sys
import os
import json
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402
from services._http import abrir_url, descrever_erro  # noqa: E402

TIMEOUT = 10
MAX_HISTORICO = 120

# chave -> (lista de símbolos Yahoo Finance candidatos, label, unidade)
INDICES_YAHOO = {
    "ibovespa":  {"simbolos": ["^BVSP"],           "unidade": "pontos", "label": "Ibovespa"},
    "sp500":     {"simbolos": ["^GSPC"],           "unidade": "pontos", "label": "S&P 500"},
    "nasdaq":    {"simbolos": ["^IXIC"],           "unidade": "pontos", "label": "Nasdaq Composite"},
    "dow_jones": {"simbolos": ["^DJI"],            "unidade": "pontos", "label": "Dow Jones"},
    "ouro":      {"simbolos": ["GC=F"],            "unidade": "US$/oz", "label": "Ouro (futuro COMEX)"},
    "petroleo":  {"simbolos": ["CL=F"],            "unidade": "US$/barril", "label": "Petróleo (WTI futuro)"},
    "vix":       {"simbolos": ["^VIX"],            "unidade": "pontos", "label": "Volatilidade (VIX)"},
}


def log(msg):
    print(f"[markets] {msg}")


def _yahoo_chart(simbolo, range_="6mo"):
    """Devolve [{"data": "YYYY-MM-DD", "valor": float}, ...] a partir do
    endpoint público de gráfico do Yahoo Finance. Sem chave/cadastro."""
    simbolo_url = urllib.parse.quote(simbolo, safe="")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{simbolo_url}?range={range_}&interval=1d"
    with abrir_url(url, timeout=TIMEOUT) as resp:
        texto = resp.read().decode("utf-8", errors="replace")
    try:
        payload = json.loads(texto)
    except json.JSONDecodeError:
        amostra = texto.strip().replace("\n", " ")[:120]
        log(f"{simbolo}: resposta não é JSON válido — trecho: {amostra!r}")
        return []
    resultados = (payload.get("chart") or {}).get("result") or []
    if not resultados:
        erro = (payload.get("chart") or {}).get("error")
        log(f"{simbolo}: sem resultado ({erro}).")
        return []
    r = resultados[0]
    timestamps = r.get("timestamp") or []
    fechamentos = ((r.get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
    out = []
    for ts, fechamento in zip(timestamps, fechamentos):
        if fechamento is None:
            continue
        data_str = __import__("datetime").datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
        out.append({"data": data_str, "valor": float(fechamento)})
    return out


def _buscar_indice(simbolos, n_dias=MAX_HISTORICO):
    ultimo_erro = None
    range_ = "1y" if n_dias > 60 else "6mo"
    for s in simbolos:
        try:
            historico = _yahoo_chart(s, range_=range_)
            if historico:
                return historico[-n_dias:]
        except Exception as e:
            ultimo_erro = e
            continue
    if ultimo_erro:
        log(f"nenhum símbolo respondeu ({simbolos}) — último erro: {descrever_erro(ultimo_erro)}")
    return []


def atualizar_indices_stooq():
    """Nome mantido (usado por players.py e pelo restante do módulo) mesmo
    após a troca de stooq -> Yahoo Finance, pra não precisar tocar em quem
    já importa essa função."""
    for chave, meta in INDICES_YAHOO.items():
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
                data_referencia=atual["data"], variacao_dia=variacao, fonte="Yahoo Finance",
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
