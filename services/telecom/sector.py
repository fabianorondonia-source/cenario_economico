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
    "base_banda_larga_brasil_ago2026": {"valor": 57.89, "unidade": "mi de acessos (+5,7% em 12 meses; Anatel pode revisar)", "fonte": "Anatel, via TELETIME (05/10/2026)"},
    "acessos_informais_estimados": {"valor": 14, "unidade": "mi de acessos/mês não reportados à Anatel (estimativa)", "fonte": "Associação Neo, via TELETIME (06/10/2026)"},
    "churn_setorial_min": {"valor": 20, "unidade": "% ao ano", "fonte": "Análises de mercado, via Baguete (13/02/2026)"},
    "churn_setorial_max": {"valor": 25, "unidade": "% ao ano", "fonte": "Análises de mercado, via Baguete (13/02/2026)"},
}

LEITURA_MOMENTO = (
    "Out/2026: a Claro fechou a compra da Desktop (01/10, ~6,2x EBITDA, EV R$4bi) — a primeira vez que "
    "uma grande tele compra um dos grandes ISPs — e a Alares concluiu a Oquei (~5,3x). Mas o mercado "
    "está dividido: na Futurecom (06/10), analistas disseram que o baixo retorno dos provedores adia a "
    "consolidação ('poucos acima de 200-300 mil assinantes ainda têm capacidade de alavancagem') e que o "
    "cenário só muda a partir de 2029; a Associação Neo estima ~14 milhões de acessos informais fora da "
    "Anatel e aponta a reforma tributária (IVA de referência 27,91%) como fator de risco e, ao mesmo "
    "tempo, catalisador de vendas. Em ago/2026 a Starlink liderou as adições (+65 mil, 936,8 mil no "
    "total) e provedores regionais cresceram pouco ou perderam base. Leitura: compradores grandes "
    "pagam prêmio por escala e base organizada, e a pressão sobre ISPs médios endividados tende a "
    "criar vendedores — bom para quem tem caixa e disciplina de diligência."
)

MOVIMENTACOES_RECENTES = [
    # valor_por_assinante: calculado por nós (EV ou valor do negócio ÷ base de
    # clientes reportada) — é assim que o mercado de ISP menor costuma
    # precificar na prática, além do múltiplo de EBITDA (que nem sempre é
    # auditado/confiável em empresas pequenas). Guardado como campo separado
    # pra virar comparável ao longo do tempo conforme mais negócios entrarem.
    {"periodo": "out/2026", "operacao": "Claro conclui a compra da Desktop (72,83% do capital) e assume o controle", "regiao": "Interior de São Paulo", "obs": "Fechado em 01/10/2026 (negócio de R$ 4bi, ~6,2x EBITDA). CEO da Claro vira presidente da Desktop; Claro protocolou oferta pública unificada para fechar o capital. Soma 12,07mi de assinantes e passa a liderar banda larga em SP (5,8mi). Primeira vez que uma grande tele compra um dos grandes ISPs.", "valor_por_assinante": "≈ R$ 3.333/assinante (EV R$4,0bi ÷ 1,2mi clientes)", "fonte": "TELETIME (01/10 e 05/10/2026)"},
    {"periodo": "out/2026", "operacao": "Alares conclui a compra da Oquei Telecom", "regiao": "Noroeste de São Paulo", "obs": "R$ 189mi (R$75,6mi à vista + 10 parcelas semestrais); Oquei: receita R$89,2mi, EBITDA R$35,5mi → ~5,3x EBITDA. Alares perdeu ~4 mil clientes em ago/2026 (base 798 mil).", "valor_por_assinante": "≈ R$ 2.779/assinante (R$189mi ÷ 68 mil clientes)", "fonte": "TELETIME (18/06 e 01/10/2026)"},
    {"periodo": "2026 (em andamento)", "operacao": "Brasil TecPar compra ativos da Ligga (354 mil assinantes)", "regiao": "Paraná", "obs": "R$ 495mi pelos ativos (R$ ~120mi à vista, resto em debêntures conversíveis) + assunção de ~R$ 1bi em debêntures da Ligga; depende de Cade, Anatel e debenturistas. TecPar vai emitir mais R$ 300mi em debêntures (28/09/2026).", "valor_por_assinante": "≈ R$ 1.397/assinante só sobre o valor pago (R$495mi ÷ 354 mil), sem contar a dívida assumida", "fonte": "Baguete/TELETIME (fev-mar e 28/09/2026)"},
    {"periodo": "out/2026", "operacao": "Unifique: controladores apresentam proposta de fechamento de capital", "regiao": "Santa Catarina", "obs": "Proposta divulgada em 05/10/2026 (detalhes de preço não conferidos). Base de 892 mil assinantes de banda larga em ago/2026.", "fonte": "TELETIME (05/10/2026)"},
    {"periodo": "jul/2026", "operacao": "América Móvil sinaliza apetite por mais aquisições de fibra", "regiao": "—", "obs": "CEO Daniel Hajj, em call de resultados: 'buscamos empresas de perfil como a Desktop, que agreguem clientes de fibra e complementem a rede'", "fonte": "TELETIME (22/07/2026)"},
    {"periodo": "2025", "operacao": "Brasil Tecpar completa 5 incorporações", "regiao": "—", "obs": "receita R$ 587,3 mi; EBITDA ajustado R$ 857 mi (+68% vs 2024)", "fonte": "TELETIME (06/03/2026)"},
    {"periodo": "2025", "operacao": "Grupo dono da Sky compra a operadora Proxxima", "regiao": "—", "fonte": "Baguete"},
]

# Os dois negócios de 2026 com dado completo (EV/preço + base de clientes)
# dão uma FAIXA real de múltiplo/valor por assinante pra comparação — mais
# robusto que um ponto único. Guardado à parte pro dashboard poder destacar
# a faixa sem precisar re-parsear o texto livre de MOVIMENTACOES_RECENTES.
FAIXA_MULTIPLOS_2026 = {
    "ev_ebitda_min": 5.3, "ev_ebitda_max": 6.2,
    "valor_assinante_min": 2779, "valor_assinante_max": 3333,
    "fonte": "Calculado sobre Claro-Desktop e Alares-Oquei Telecom (TELETIME, mar e jun/2026)",
}

# FUST (Fundo de Universalização dos Serviços de Telecomunicações) — fonte de
# crédito/subsídio pra expansão de rede rural, cada vez mais relevante pro
# perfil da Netway (provedor regional em área pouco atendida). Curadoria
# manual — não é um valor único, é um resumo de oportunidade/janela.
FUST_RESUMO = {
    "orcamento_2025_mobilizado": "R$ 3,2bi mobilizados em 2025 (R$ 2bi já aprovados via BNDES, beneficiando 923 municípios e 479 provedores regionais)",
    "orcamento_2026": "R$ 1,28bi",
    "orcamento_2027_projetado": "R$ 3,87bi (proposta aprovada pelo Conselho Gestor — alta de 201,6% vs 2026)",
    "janela_beneficio_fiscal": "Alíquota reduzida de 1% para 0,5% pra quem investe direto em conectividade (Lei 14.173/2021) VENCE no fim de 2026 — janela de decisão neste ano",
    "programa_regional": "PL 3211/25 (aprovado na Comissão de Comunicação da Câmara em abr/2026) cria o Programa Nacional de Incentivo aos Provedores Regionais: prioridade em crédito de bancos públicos + recursos do Fust + editais de infraestrutura em áreas rurais/pouco atendidas. Define 'provedor regional' como quem tem <5% de participação nacional em cada mercado — a Netway se enquadraria.",
    "situacao_atual": "Ainda tramitando: falta aprovação do PLP 230/2025 (impede contingenciamento fiscal do Fust) e do próprio PL 3211/25 nas comissões de Finanças/CCJ + plenário da Câmara e Senado. Dinheiro existe mas execução ainda esbarra em entraves orçamentários (LRF art. 9º).",
}
FONTE_FUST = "TELETIME (13/07/2026, 'paradoxo do Fust') + IPNews (24/04/2026, tramitação PL 3211/25)"

RISCOS_REGULATORIOS = [
    "Fim da dispensa automática de outorga (Res. 777/2025, RGO art. 13): provedores que operavam sem outorga formal (até 5 mil assinantes) agora precisam regularizar a autorização junto à Anatel sob risco de multa/paralização — checar isso na due diligence de qualquer ISP-alvo de aquisição.",
    "Novo PGMC (Plano Geral de Metas de Competição) enfraquece as ORPAs (Ofertas de Referência Pública de Atacado): Abrint e TelComp alertam para risco de concentração de mercado e cláusulas mais duras das grandes operadoras nas negociações de atacado com provedores regionais.",
    "Compartilhamento de postes segue em disputa: Decreto 12.068/2024 em revisão pela Anatel desde dez/2025, e o PL 3.220/2019 (novo marco de preço/regras) tramitando — aprovado na CCJ do Senado em abr/2026, ainda em análise na Câmara.",
    "Reforma tributária: com a alíquota de referência do IVA estimada em 27,91%, a carga sobre o setor deve subir e muitos provedores não estão preparados para aplicar o cashback previsto; a Anatel vê o split payment como possível catalisador de consolidação (Futurecom, 06/10/2026). Também pesa na diligência: informalidade (~14 mi de acessos fora da Anatel) e relatos de cidades com ~50% da banda larga sob influência de facções.",
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
        fonte="TELETIME/Baguete (atualizado 07/10/2026)", atualizacao="manual", historico=MOVIMENTACOES_RECENTES
    )
    db.upsert_indicador(
        chave="telecom_riscos_regulatorios", categoria="telecom_setor", valor=None, unidade="lista",
        fonte="Anatel/Abrint/TelComp/Associação Neo (atualizado 07/10/2026)", atualizacao="manual",
        historico=[{"risco": r} for r in RISCOS_REGULATORIOS]
    )
    db.upsert_indicador(
        chave="telecom_faixa_multiplos", categoria="telecom_setor", valor=None, unidade="faixa",
        fonte=FAIXA_MULTIPLOS_2026["fonte"], atualizacao="manual", historico=[FAIXA_MULTIPLOS_2026]
    )
    db.upsert_indicador(
        chave="telecom_fust", categoria="telecom_setor", valor=None, unidade="resumo",
        fonte=FONTE_FUST, atualizacao="manual", historico=[FUST_RESUMO]
    )
    print("[telecom.sector] dados do setor de provedores carregados no cache.")


if __name__ == "__main__":
    atualizar_todos()
