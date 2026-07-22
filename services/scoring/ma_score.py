"""
"M&A Score" — score 0-100 específico para "é bom momento pra comprar
provedores regionais?", conforme pedido do Fabiano. Fatores: mercado, juros,
liquidez, valuation (múltiplo EV/EBITDA do setor), quantidade de transações
recentes, apetite dos fundos, disponibilidade de crédito.

"Apetite dos fundos" não tem fonte pública gratuita — usamos um proxy fixo
neutro (50) até que exista um dado real pra substituir (editável aqui).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402

FAIXAS = [
    (75, "Excelente momento para comprar provedores", "🟢", "excelente"),
    (55, "Momento razoável", "🟡", "razoavel"),
    (35, "Aguarde", "🟠", "aguarde"),
    (0,  "Não recomendado", "🔴", "nao_recomendado"),
]


def _nota_faixa(valor, faixas):
    for limite, nota in faixas:
        if valor <= limite:
            return nota
    return faixas[-1][1]


def calcular():
    ind = db.get_todos_indicadores()
    componentes = []

    # Mercado: tendência recente do Ibovespa (proxy de apetite geral por risco)
    ibov_var = ind.get("ibovespa", {}).get("variacao_dia")
    if ibov_var is not None:
        nota = 75 if ibov_var >= 0 else _nota_faixa(abs(ibov_var), [(1, 55), (3, 35), (999, 15)])
        componentes.append({"nome": "Mercado (Ibovespa)", "nota": nota, "peso": 0.8})

    # Juros: Selic alta encarece financiamento da aquisição
    selic = ind.get("selic_meta", {}).get("valor")
    if selic is not None:
        nota = _nota_faixa(selic, [(8, 95), (11, 65), (14, 35), (999, 10)])
        componentes.append({"nome": "Juros (custo de financiamento)", "nota": nota, "peso": 1.3})

    # Liquidez / disponibilidade de crédito
    inadimplencia = ind.get("inadimplencia", {}).get("valor")
    spread = ind.get("spread_bancario", {}).get("valor")
    if inadimplencia is not None:
        nota_inad = _nota_faixa(inadimplencia, [(3, 85), (5, 60), (7, 35), (999, 15)])
        componentes.append({"nome": "Inadimplência do sistema", "nota": nota_inad, "peso": 0.7})
    if spread is not None:
        nota_spread = _nota_faixa(spread, [(15, 80), (25, 55), (35, 30), (999, 15)])
        componentes.append({"nome": "Spread bancário", "nota": nota_spread, "peso": 0.6})

    # Valuation: múltiplo EV/EBITDA baixo = barato para comprador
    multiplo = ind.get("multiplo_ev_ebitda_atual", {}).get("valor")
    if multiplo is not None:
        nota = _nota_faixa(multiplo, [(5, 95), (8, 70), (12, 45), (999, 20)])
        componentes.append({"nome": "Valuation (múltiplo EV/EBITDA)", "nota": nota, "peso": 1.5})

    # Quantidade de transações recentes = mercado aquecido (mais liquidez pra negociar)
    movs = ind.get("telecom_movimentacoes", {}).get("historico") or []
    n_movs = len(movs) if isinstance(movs, list) else 0
    nota_movs = _nota_faixa(n_movs, [(1, 30), (3, 55), (6, 75), (999, 90)])
    componentes.append({"nome": "Atividade de M&A recente", "nota": nota_movs, "peso": 0.9})

    # Apetite dos fundos — sem fonte pública gratuita; proxy neutro editável
    componentes.append({"nome": "Apetite dos fundos (proxy manual)", "nota": 50, "peso": 0.5})

    if not componentes:
        return {"score": None, "nivel": "Dados insuficientes", "emoji": "⚪", "chave_nivel": "indefinido", "componentes": []}

    soma_pesos = sum(c["peso"] for c in componentes)
    score = round(sum(c["nota"] * c["peso"] for c in componentes) / soma_pesos)

    for limite, texto, emoji, chave in FAIXAS:
        if score >= limite:
            return {"score": score, "nivel": texto, "emoji": emoji, "chave_nivel": chave, "componentes": componentes}
    return {"score": score, "nivel": "Não recomendado", "emoji": "🔴", "chave_nivel": "nao_recomendado", "componentes": componentes}


if __name__ == "__main__":
    import json
    print(json.dumps(calcular(), ensure_ascii=False, indent=2))
