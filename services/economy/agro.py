"""
Contexto econômico regional (RO/MT/TO/PA/MS) via preço de commodities
agropecuárias — soja e boi gordo.

Por que isso está aqui: o painel inteiro (Selic, IPCA, Ibovespa etc.) mede
a economia NACIONAL, mas o poder de compra do assinante potencial nos
estados de atuação da Netway está muito mais ligado ao ciclo do agronegócio
regional (safra, preço da arroba/saca) do que ao IPCA nacional — em
municípios do interior de MT/RO/TO/PA/MS, boa parte da renda circula em
torno da cadeia da soja e da pecuária. Preço de commodity em alta = mais
renda disponível na praça = melhor ARPU potencial/menor churn; preço em
queda = pressão de inadimplência num município agro-dependente.

Fonte: CEPEA-Esalq/USP (referência oficial nacional para soja e para o
indicador Boi Gordo Cepea/B3, usado até como lastro dos contratos futuros
na B3). CEPEA não tem API pública nem endpoint JSON sem chave (site é
renderizado via JS/ASPX, widget também não expõe um feed simples) — os
valores abaixo foram coletados via notícias que citam o Indicador Cepea
diretamente, com data explícita. Atualização manual, igual a sector.py:
revisar periodicamente (o preço de commodity agrícola oscila bem mais
rápido que os indicadores macro nacionais, então esse é o campo do painel
que mais precisa de refresh frequente).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402

AGRO = {
    "soja_saca": {
        "valor": 144.17, "unidade": "R$/saca (60kg)",
        "fonte": "CEPEA/Esalq-USP, Paranaguá-PR, via Notícias Agrícolas (22/07/2026)",
        "contexto": "Alta de 0,77% no dia; média de julho (R$139,1/saca até dia 17) é o maior patamar médio de 2026 e 2,2% acima do fechamento de 2025.",
    },
    "boi_gordo_arroba_mt": {
        "valor": 311.52, "unidade": "R$/arroba (Mato Grosso)",
        "fonte": "CEPEA/Esalq-USP, via Portal DBO (3ª semana de 07/2026)",
        "contexto": "Queda de 7,94% na 3ª semana de julho — reflexo de incerteza nas cotas de exportação da China, mercado relevante para os frigoríficos do MT. Referência nacional Cepea estava em R$329,2/arroba em 15/07/2026.",
    },
}


def log(msg):
    print(f"[economy.agro] {msg}")


def atualizar_todos():
    for chave, meta in AGRO.items():
        db.upsert_indicador(
            chave=chave, categoria="agro_regional", valor=meta["valor"], unidade=meta["unidade"],
            fonte=meta["fonte"], atualizacao="manual",
            historico=[{"contexto": meta["contexto"]}]
        )
        log(f"{chave}: {meta['valor']} {meta['unidade']}")


if __name__ == "__main__":
    atualizar_todos()
