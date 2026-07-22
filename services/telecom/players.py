"""
Grandes grupos do setor de conectividade citados pelo Fabiano. Para os
grupos de capital aberto, buscamos cotação real (Yahoo Finance, gratuito,
sem chave — trocado de stooq.com porque stooq bloqueia requisições vindas
de IP de nuvem/datacenter, como as do GitHub Actions) como termômetro de
mercado. Para os de capital fechado, mantemos só o perfil curado
(segmento/região) — não existe dado público de mercado para eles, e não
inventamos números de faturamento/clientes que não temos fonte para
confirmar.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services", "indicators"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402
from services.indicators.markets import _buscar_indice  # noqa: E402
from services._http import descrever_erro  # noqa: E402

GRUPOS = {
    "Brisanet":     {"tipo": "capital aberto (B3: BRIT3)", "simbolos_stooq": ["BRIT3.SA"], "segmento": "FTTH + 5G FWA — Nordeste"},
    "Unifique":     {"tipo": "capital aberto (B3: FIQE3)", "simbolos_stooq": ["FIQE3.SA"], "segmento": "FTTH — Sul do Brasil"},
    "American Tower": {"tipo": "capital aberto (NYSE: AMT)", "simbolos_stooq": ["AMT"], "segmento": "Infraestrutura de torres"},
    "IHS Holding":  {"tipo": "capital aberto (NYSE: IHS)", "simbolos_stooq": ["IHS"], "segmento": "Infraestrutura de torres — África e Brasil"},
    "Desktop":      {"tipo": "capital fechado", "simbolos_stooq": [], "segmento": "FTTH — interior de São Paulo"},
    "Vero":         {"tipo": "capital fechado", "simbolos_stooq": [], "segmento": "FTTH — atuação nacional (plataforma multirregional)"},
    "Ligga":        {"tipo": "capital fechado (origem Copel Telecom)", "simbolos_stooq": [], "segmento": "FTTH — Sul do Brasil"},
    "Mhnet":        {"tipo": "capital fechado", "simbolos_stooq": [], "segmento": "FTTH — Centro-Oeste (Mato Grosso)"},
    "Brasil Tecpar": {"tipo": "capital fechado — plataforma de consolidação (roll-up)", "simbolos_stooq": [], "segmento": "Aquisição/integração de ISPs regionais"},
    "Algar Telecom": {"tipo": "capital fechado (Grupo Algar)", "simbolos_stooq": [], "segmento": "Telecom completa — Triângulo Mineiro e regiões"},
    "V.tal":        {"tipo": "infraestrutura atacadista (joint-venture ex-Oi)", "simbolos_stooq": [], "segmento": "Rede neutra de fibra — atacado"},
    "Fibrasil":     {"tipo": "joint-venture (TIM + FiberCo)", "simbolos_stooq": [], "segmento": "Rede neutra de fibra — atacado"},
    "Neutral Networks": {"tipo": "joint-venture / rede neutra", "simbolos_stooq": [], "segmento": "Rede neutra regional"},
}


def log(msg):
    print(f"[telecom.players] {msg}")


def atualizar_todos():
    for nome, meta in GRUPOS.items():
        chave = "grupo_" + nome.lower().replace(" ", "_").replace(".", "")
        cotacao = None
        variacao = None
        data_ref = None
        if meta["simbolos_stooq"]:
            try:
                historico = _buscar_indice(meta["simbolos_stooq"], n_dias=60)
                if historico:
                    atual = historico[-1]
                    anterior = historico[-2] if len(historico) > 1 else None
                    cotacao = atual["valor"]
                    data_ref = atual["data"]
                    if anterior and anterior["valor"]:
                        variacao = round(((atual["valor"] - anterior["valor"]) / anterior["valor"]) * 100, 2)
            except Exception as e:
                log(f"{nome}: falhou ao buscar cotação ({descrever_erro(e)}).")

        db.upsert_indicador(
            chave=chave, categoria="telecom_grupos", valor=cotacao,
            unidade="cotação (última)" if cotacao else meta["tipo"],
            data_referencia=data_ref, variacao_dia=variacao,
            fonte="Yahoo Finance" if cotacao else "Perfil curado — sem dado público de mercado",
            atualizacao="automatica" if meta["simbolos_stooq"] else "manual",
            historico=[{"nome": nome, "tipo": meta["tipo"], "segmento": meta["segmento"]}]
        )
        log(f"{nome}: {'cotação ' + str(cotacao) if cotacao else 'perfil curado (capital fechado)'}")


if __name__ == "__main__":
    atualizar_todos()
