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
    # Antes era uma média genérica de mercado (Alvarez & Marsal, fev/2026).
    # Trocado pelo múltiplo real do maior negócio do ano até agora (Claro
    # comprando a Desktop, mar/2026) — mais concreto e verificável que uma
    # média de consultoria, e mostra que o mercado pagou ACIMA da faixa em
    # que a Desktop vinha negociando (~4,5-5,0x) por um ativo de escala.
    "multiplo_ev_ebitda_atual": {"valor": 6.2, "unidade": "x EBITDA (negócio Claro→Desktop)", "fonte": "TELETIME/XP Investimentos — Claro compra 73% da Desktop, EV R$ 4,0bi (22-23/03/2026)"},
    "multiplo_ev_ebitda_2021":  {"valor": 16, "unidade": "x EBITDA", "fonte": "Alvarez & Marsal, via Baguete (13/02/2026)"},
    "participacao_isps_banda_larga": {"valor": 56, "unidade": "% do mercado de banda larga fixa", "fonte": "Anatel, via Inforchannel (26/06/2026)"},
    "crescimento_assinantes_2018_2025": {"valor": 72, "unidade": "% acumulado (31,2mi → 53,8mi)", "fonte": "Anatel, via Baguete (13/02/2026)"},
    "crescimento_assinantes_2024_2025": {"valor": 2.5, "unidade": "% no período (52,54mi → 53,88mi)", "fonte": "Anatel, via TELETIME (02/02/2026)"},
    "churn_setorial_min": {"valor": 20, "unidade": "% ao ano", "fonte": "Análises de mercado, via Baguete (13/02/2026)"},
    "churn_setorial_max": {"valor": 25, "unidade": "% ao ano", "fonte": "Análises de mercado, via Baguete (13/02/2026)"},
}

LEITURA_MOMENTO = (
    "2026 confirma o ponto de inflexão: crescimento orgânico de assinantes esgotado (+2,5% ao ano) "
    "coexiste agora com um mercado de M&A visivelmente reaquecido — a Claro pagou 6,2x EBITDA pela "
    "Desktop (mar/2026, EV R$4bi), acima da faixa de 4,5-5,0x em que o ativo vinha negociando, e a "
    "controladora América Móvil confirmou publicamente (22/07/2026) que segue caçando mais ativos com "
    "o mesmo perfil (fibra, clientes que complementem a rede). Ou seja: o desconto dos múltiplos de "
    "2021-2025 não significa mais 'ativo barato parado na prateleira' — grandes compradores estão "
    "pagando prêmio por escala e qualidade de base. Por outro lado, o churn setorial de 20-25% ao ano "
    "mostra que isso vale para ativos organizados; base desorganizada continua descontada."
)

MOVIMENTACOES_RECENTES = [
    {"periodo": "mar/2026", "operacao": "Claro (América Móvil) compra 73% da Desktop", "regiao": "Interior de São Paulo", "obs": "EV R$ 4,0bi incl. dívida (~6,2x EBITDA 2025); Anatel já aprovou, falta Cade para fechar em 2026", "fonte": "TELETIME (22-23/03/2026)"},
    {"periodo": "jul/2026", "operacao": "América Móvil sinaliza apetite por mais aquisições de fibra", "regiao": "—", "obs": "CEO Daniel Hajj, em call de resultados: 'buscamos empresas de perfil como a Desktop, que agreguem clientes de fibra e complementem a rede'", "fonte": "TELETIME (22/07/2026)"},
    {"periodo": "jun/2026", "operacao": "Alares compra Oquei Telecom", "regiao": "São Paulo", "obs": "R$ 189 milhões", "fonte": "TELETIME (18/06/2026)"},
    {"periodo": "2025", "operacao": "Brasil Tecpar completa 5 incorporações", "regiao": "—", "obs": "receita R$ 587,3 mi; EBITDA ajustado R$ 857 mi (+68% vs 2024)", "fonte": "TELETIME (06/03/2026)"},
    {"periodo": "2025", "operacao": "Grupo dono da Sky compra a operadora Proxxima", "regiao": "—", "fonte": "Baguete"},
]

RISCOS_REGULATORIOS = [
    "Fim da dispensa automática de outorga (Res. 777/2025, RGO art. 13): provedores que operavam sem outorga formal (até 5 mil assinantes) agora precisam regularizar a autorização junto à Anatel sob risco de multa/paralização — checar isso na due diligence de qualquer ISP-alvo de aquisição.",
    "Novo PGMC (Plano Geral de Metas de Competição) enfraquece as ORPAs (Ofertas de Referência Pública de Atacado): Abrint e TelComp alertam para risco de concentração de mercado e cláusulas mais duras das grandes operadoras nas negociações de atacado com provedores regionais.",
    "Compartilhamento de postes segue em disputa: Decreto 12.068/2024 em revisão pela Anatel desde dez/2025, e o PL 3.220/2019 (novo marco de preço/regras) tramitando — aprovado na CCJ do Senado em abr/2026, ainda em análise na Câmara.",
    "Fiscalização mais dura sobre retenção de logs (Marco Civil da Internet): decisões recentes do STJ reforçam a obrigação de guardar IP + porta lógica + timestamp por 1 ano — provedor sem CGNAT/IPv6 auditado corre risco de responder por identificação que falhou.",
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
        fonte="TELETIME/Baguete (atualizado 22/07/2026)", atualizacao="manual", historico=MOVIMENTACOES_RECENTES
    )
    db.upsert_indicador(
        chave="telecom_riscos_regulatorios", categoria="telecom_setor", valor=None, unidade="lista",
        fonte="Anatel/SCM Engenharia/Abrint/TelComp (atualizado 22/07/2026)", atualizacao="manual",
        historico=[{"risco": r} for r in RISCOS_REGULATORIOS]
    )
    print("[telecom.sector] dados do setor de provedores carregados no cache.")


if __name__ == "__main__":
    atualizar_todos()
