"""
"Momento de Investimento" — score 0-100 que resume se o cenário macro
favorece investir/expandir no Brasil agora.

Determinístico (sem IA generativa): cada componente vira uma nota 0-100 por
faixas de valor (thresholds abaixo), e o score final é a média ponderada.
Pesos e faixas são um ponto de partida editável — ajuste conforme a visão
de risco do Fabiano.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402

NIVEIS = [
    (70, "Excelente momento", "excelente"),
    (55, "Bom momento", "bom"),
    (40, "Momento neutro", "neutro"),
    (25, "Cautela", "cautela"),
    (0,  "Alto risco", "alto_risco"),
]


def _nota_faixa(valor, faixas):
    """faixas: lista de (limite_superior_inclusive, nota) ordenada crescente por valor."""
    for limite, nota in faixas:
        if valor <= limite:
            return nota
    return faixas[-1][1]


def calcular():
    ind = db.get_todos_indicadores()
    componentes = []

    selic = ind.get("selic_meta", {}).get("valor")
    if selic is not None:
        nota = _nota_faixa(selic, [(8, 100), (11, 70), (14, 40), (999, 15)])
        componentes.append({"nome": "Selic (custo de capital)", "nota": nota, "peso": 1.2})

    cds = ind.get("risco_pais_cds", {}).get("valor")
    if cds is not None:
        nota = _nota_faixa(cds, [(130, 90), (180, 65), (250, 40), (9999, 15)])
        componentes.append({"nome": "Risco-país (CDS)", "nota": nota, "peso": 1.2})

    ipca12 = ind.get("ipca_12m", {}).get("valor")
    if ipca12 is not None:
        nota = _nota_faixa(ipca12, [(4.5, 85), (6, 55), (8, 30), (999, 10)])
        componentes.append({"nome": "Inflação (IPCA 12m)", "nota": nota, "peso": 0.8})

    dolar_var = ind.get("dolar_ptax", {}).get("variacao_dia")
    if dolar_var is not None:
        nota = _nota_faixa(abs(dolar_var), [(0.3, 80), (1, 55), (999, 25)])
        componentes.append({"nome": "Estabilidade cambial", "nota": nota, "peso": 0.6})

    ibov_var = ind.get("ibovespa", {}).get("variacao_dia")
    if ibov_var is not None:
        nota = 80 if ibov_var >= 0 else _nota_faixa(abs(ibov_var), [(1, 60), (3, 40), (999, 15)])
        componentes.append({"nome": "Bolsa (Ibovespa)", "nota": nota, "peso": 0.7})

    if not componentes:
        return {"score": None, "nivel": "Dados insuficientes", "chave_nivel": "indefinido", "componentes": []}

    soma_pesos = sum(c["peso"] for c in componentes)
    score = round(sum(c["nota"] * c["peso"] for c in componentes) / soma_pesos)

    for limite, texto, chave in NIVEIS:
        if score >= limite:
            return {"score": score, "nivel": texto, "chave_nivel": chave, "componentes": componentes}
    return {"score": score, "nivel": "Alto risco", "chave_nivel": "alto_risco", "componentes": componentes}


if __name__ == "__main__":
    import json
    print(json.dumps(calcular(), ensure_ascii=False, indent=2))
