"""
Gerador de "insights" em texto — 100% determinístico (regras if/then sobre
os indicadores), sem chamada a nenhum modelo de IA generativa. Cada regra
observa uma combinação de indicadores e, se as condições baterem, produz
uma frase pronta, no mesmo espírito dos exemplos do Fabiano:

  "O aumento do CDS Brasil junto com alta do dólar e juros indica maior
   risco para operações financiadas."
  "O mercado apresenta redução no múltiplo médio de valuation dos ISPs,
   favorecendo aquisições."
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402


def _get(ind, chave, campo="valor"):
    d = ind.get(chave)
    return d.get(campo) if d else None


def gerar_insights():
    ind = db.get_todos_indicadores()
    insights = []

    cds = _get(ind, "risco_pais_cds")
    dolar_var = _get(ind, "dolar_ptax", "variacao_dia")
    selic = _get(ind, "selic_meta")
    if cds is not None and cds > 200 and dolar_var is not None and dolar_var > 0.5 and selic is not None and selic > 12:
        insights.append({
            "tipo": "risco",
            "texto": "O risco-país elevado, combinado com alta do dólar e juros ainda restritivos, "
                     "aponta maior risco para operações financiadas — o custo de capital para aquisições sobe."
        })
    elif cds is not None and cds < 140 and selic is not None and selic <= 11:
        insights.append({
            "tipo": "oportunidade",
            "texto": "Risco-país controlado e juros em patamar mais baixo reduzem o custo de financiamento "
                     "de operações de M&A — janela mais favorável para captar recursos."
        })

    multiplo = _get(ind, "multiplo_ev_ebitda_atual")
    multiplo_2021 = _get(ind, "multiplo_ev_ebitda_2021")
    if multiplo is not None and multiplo_2021 is not None and multiplo < multiplo_2021 * 0.6:
        insights.append({
            "tipo": "oportunidade",
            "texto": f"O mercado apresenta múltiplo médio de valuation dos ISPs em {multiplo}x EBITDA, "
                     f"bem abaixo dos {multiplo_2021}x praticados em 2021 — cenário que favorece aquisições "
                     f"para quem tem capital disponível."
        })

    crescimento_recente = _get(ind, "crescimento_assinantes_2024_2025")
    if crescimento_recente is not None and crescimento_recente < 5:
        insights.append({
            "tipo": "contexto",
            "texto": f"O crescimento orgânico de assinantes de banda larga desacelerou para {crescimento_recente}% "
                     f"no período mais recente — expansão via M&A tende a ganhar peso frente ao crescimento orgânico."
        })

    ibov_var = _get(ind, "ibovespa", "variacao_dia")
    if ibov_var is not None and ibov_var <= -3:
        insights.append({
            "tipo": "risco",
            "texto": f"O Ibovespa recuou {abs(ibov_var):.1f}% no último pregão registrado — sinal de aversão "
                     f"a risco que costuma preceder maior cautela em operações de crédito e M&A."
        })

    ipca12 = _get(ind, "ipca_12m")
    if ipca12 is not None and ipca12 > 6:
        insights.append({
            "tipo": "risco",
            "texto": f"A inflação acumulada em 12 meses está em {ipca12}%, acima da meta — pressão para "
                     f"manutenção de juros altos por mais tempo, encarecendo novas captações."
        })

    inadimplencia = _get(ind, "inadimplencia")
    if inadimplencia is not None and inadimplencia > 6:
        insights.append({
            "tipo": "risco",
            "texto": f"A inadimplência do sistema de crédito está em {inadimplencia}%, nível elevado que "
                     f"tende a deixar bancos mais seletivos na concessão de crédito para aquisições."
        })

    n_movs = len(_get(ind, "telecom_movimentacoes", "historico") or [])
    if n_movs >= 4:
        insights.append({
            "tipo": "contexto",
            "texto": f"Foram registradas {n_movs} movimentações relevantes de M&A no setor recentemente — "
                     f"mercado de consolidação de ISPs segue ativo."
        })

    if not insights:
        insights.append({
            "tipo": "contexto",
            "texto": "Ainda não há dados suficientes carregados para gerar leituras automáticas — rode a "
                     "atualização de indicadores primeiro."
        })

    return insights


if __name__ == "__main__":
    import json
    print(json.dumps(gerar_insights(), ensure_ascii=False, indent=2))
