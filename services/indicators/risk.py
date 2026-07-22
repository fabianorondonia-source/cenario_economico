"""
Risco-país, rating soberano e curva de juros — NÃO existe fonte pública
gratuita e em tempo real para isso:

  - O EMBI+ (JPMorgan) foi descontinuado pelo Ipeadata em jul/2024. O mercado
    passou a usar o CDS soberano de 5 anos como referência, mas CDS em tempo
    real é dado de terminal pago (Bloomberg/Refinitiv).
  - Rating soberano (S&P/Moody's/Fitch) só muda algumas vezes por ano e não
    tem API — é notícia.
  - Curva de juros (DI futuro) é dado da B3, também sem endpoint gratuito
    simples e estável.

Por isso este módulo é curadoria manual: os valores abaixo devem ser
revisados periodicamente (pesquisa de mercado) e atualizados aqui à mão —
eles alimentam o cache do mesmo jeito que os módulos automáticos, só que
sem um fetch de rede por trás.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402

DADOS_MANUAIS = {
    "risco_pais_cds": {
        "valor": 116, "unidade": "pontos (CDS soberano 5 anos)",
        "data_referencia": "maio/2026",
        "fonte": "Poder360 — menor nível no 3º mandato de Lula. EMBI+ descontinuado pelo Ipeadata em jul/2024.",
    },
    "rating_sp":     {"valor": "BB-",  "unidade": "rating", "data_referencia": "2026", "fonte": "S&P Global Ratings"},
    "rating_moodys": {"valor": "Ba1",  "unidade": "rating", "data_referencia": "mai/2025 (outlook estável)", "fonte": "Moody's — elevado de Ba2 para Ba1 em out/2024"},
    "rating_fitch":  {"valor": "BB",   "unidade": "rating", "data_referencia": "2026", "fonte": "Fitch Ratings"},
    "grau_investimento": {"valor": False, "unidade": "bool", "data_referencia": "2026", "fonte": "Grau de investimento começa em BBB-/Baa3 — Brasil está abaixo"},
    "pib_projecao_min": {"valor": 1.6, "unidade": "%", "data_referencia": "2026", "fonte": "Ipea (1,6%) / Fitch (2,1%) / SPE-Fazenda (2,3%)"},
    "pib_projecao_max": {"valor": 2.3, "unidade": "%", "data_referencia": "2026", "fonte": "Ipea (1,6%) / Fitch (2,1%) / SPE-Fazenda (2,3%)"},
    "ipca_projecao_min": {"valor": 4.2, "unidade": "%", "data_referencia": "2026", "fonte": "Ipea (4,2%) / ONU (4,3%) / Itaú BBA (5,4%)"},
    "ipca_projecao_max": {"valor": 5.4, "unidade": "%", "data_referencia": "2026", "fonte": "Ipea (4,2%) / ONU (4,3%) / Itaú BBA (5,4%)"},
}


def atualizar_todos():
    for chave, meta in DADOS_MANUAIS.items():
        db.upsert_indicador(
            chave=chave, categoria="risco", valor=meta["valor"] if isinstance(meta["valor"], (int, float)) else None,
            unidade=meta["unidade"], data_referencia=meta["data_referencia"], fonte=meta["fonte"],
            atualizacao="manual"
        )
        # valores não numéricos (rating em letra, booleano) ficam só no histórico_json como registro bruto
        if not isinstance(meta["valor"], (int, float)):
            db.upsert_indicador(
                chave=chave, categoria="risco", valor=None, unidade=meta["unidade"],
                data_referencia=meta["data_referencia"], fonte=meta["fonte"], atualizacao="manual",
                historico=[{"valor_texto": meta["valor"]}]
            )
    print("[risk] indicadores manuais (risco-país, rating, projeções) carregados no cache.")


if __name__ == "__main__":
    atualizar_todos()
