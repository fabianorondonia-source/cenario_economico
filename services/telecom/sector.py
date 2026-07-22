"""
Setor de provedores de internet (ISPs) — múltiplos de M&A, participação de
mercado, churn, movimentações recentes e riscos regulatórios.

Não existe API pública para múltiplos de M&A ou dados agregados de ISPs
regionais — este módulo é curadoria manual, com fonte e data em cada campo.
Revisar periodicamente (pesquisa de mercado / notícias do setor).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402

SETOR = {
    "multiplo_ev_ebitda_atual": {"valor": 4, "unidade": "x EBITDA", "fonte": "Alvarez & Marsal, via Baguete (13/02/2026)"},
    "multiplo_ev_ebitda_2021":  {"valor": 16, "unidade": "x EBITDA", "fonte": "Alvarez & Marsal, via Baguete (13/02/2026)"},
    "participacao_isps_banda_larga": {"valor": 56.4, "unidade": "% do mercado de banda larga fixa", "fonte": "Anatel, via IPNews (22/12/2025)"},
    "crescimento_assinantes_2018_2025": {"valor": 72, "unidade": "% acumulado (31,2mi → 53,8mi)", "fonte": "Anatel, via Baguete (13/02/2026)"},
    "crescimento_assinantes_2024_2025": {"valor": 2.5, "unidade": "% no período", "fonte": "Anatel, via Baguete (13/02/2026)"},
    "churn_setorial_min": {"valor": 20, "unidade": "% ao ano", "fonte": "Análises de mercado, via Baguete (13/02/2026)"},
    "churn_setorial_max": {"valor": 25, "unidade": "% ao ano", "fonte": "Análises de mercado, via Baguete (13/02/2026)"},
}

LEITURA_MOMENTO = (
    "2026 é apontado pelo mercado como ponto de inflexão: crescimento orgânico de assinantes esgotado "
    "(+2,5% ao ano) somado a múltiplos historicamente baixos (~4x EBITDA vs ~16x em 2021) tornam a "
    "aquisição de provedores regionais relativamente barata para quem tem capital e disciplina de "
    "integração. Por outro lado, o mercado penaliza compras de base sem padronização técnica e "
    "governança — o churn setorial de 20-25% ao ano mostra que ativo barato nem sempre é ativo bom."
)

MOVIMENTACOES_RECENTES = [
    {"periodo": "2026", "operacao": "Alares compra Ipnet Telecom", "regiao": "Interior de São Paulo", "fonte": "Baguete/IPNews"},
    {"periodo": "2026", "operacao": "TIP Brasil compra TA Telecom", "regiao": "Telefonia móvel", "obs": "meta de 500 mil clientes móveis ativos até 2026", "fonte": "IPNews"},
    {"periodo": "2026", "operacao": "Altarede e K2 Telecom anunciam fusão", "regiao": "—", "fonte": "IPNews"},
    {"periodo": "2025", "operacao": "Brasil Tecpar completa 5 incorporações", "regiao": "—", "obs": "receita R$ 587,3 mi; EBITDA ajustado R$ 857 mi (+68% vs 2024)", "fonte": "TELETIME (06/03/2026)"},
    {"periodo": "2025", "operacao": "Grupo dono da Sky compra a operadora Proxxima", "regiao": "—", "fonte": "Baguete"},
]

RISCOS_REGULATORIOS = [
    "Tarifa antidumping pode elevar o preço da fibra óptica importada, pressionando o custo de expansão de rede.",
    "Disputa Anatel x Aneel sobre compartilhamento de postes — Aneel aprovou proposta própria e devolveu o tema à Anatel.",
    "Reavaliação do PGMC (Plano Geral de Metas de Competição) pela Anatel gera receio de retrocesso regulatório, segundo a associação Neo.",
]


def atualizar_todos():
    for chave, meta in SETOR.items():
        db.upsert_indicador(
            chave=chave, categoria="telecom_setor", valor=meta["valor"], unidade=meta["unidade"],
            fonte=meta["fonte"], atualizacao="manual"
        )
    db.upsert_indicador(
        chave="telecom_leitura_momento", categoria="telecom_setor", valor=None, unidade="texto",
        fonte="Curadoria Netway", atualizacao="manual", historico=[{"texto": LEITURA_MOMENTO}]
    )
    db.upsert_indicador(
        chave="telecom_movimentacoes", categoria="telecom_setor", valor=None, unidade="lista",
        fonte="Baguete/IPNews/TELETIME", atualizacao="manual", historico=MOVIMENTACOES_RECENTES
    )
    db.upsert_indicador(
        chave="telecom_riscos_regulatorios", categoria="telecom_setor", valor=None, unidade="lista",
        fonte="IPNews", atualizacao="manual", historico=[{"risco": r} for r in RISCOS_REGULATORIOS]
    )
    print("[telecom.sector] dados do setor de provedores carregados no cache.")


if __name__ == "__main__":
    atualizar_todos()
