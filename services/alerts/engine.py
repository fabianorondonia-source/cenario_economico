"""
Motor de alertas por threshold — thresholds configuráveis em config/settings.json.
Só grava um novo registro em alertas_log quando o alerta MUDA de estado
(inativo -> ativo), evitando log duplicado a cada atualização.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "settings.json")


def _carregar_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _get(ind, chave, campo="valor"):
    d = ind.get(chave)
    return d.get(campo) if d else None


def avaliar():
    cfg = _carregar_config().get("alertas", {})
    ind = db.get_todos_indicadores()
    regras = []

    dolar = _get(ind, "dolar_ptax")
    if dolar is not None:
        regras.append(("dolar_alto", dolar > cfg.get("dolar_max", 6.0),
                        f"🚨 Dólar acima de R$ {cfg.get('dolar_max', 6.0):.2f} (atual: R$ {dolar:.2f})", "critico"))

    selic = _get(ind, "selic_meta")
    if selic is not None:
        regras.append(("selic_alta", selic > cfg.get("selic_max", 15.0),
                        f"🚨 Selic acima de {cfg.get('selic_max', 15.0)}% (atual: {selic}%)", "atencao"))

    cds = _get(ind, "risco_pais_cds")
    if cds is not None:
        regras.append(("cds_alto", cds > cfg.get("cds_max", 300),
                        f"🚨 CDS Brasil acima de {cfg.get('cds_max', 300)} pontos (atual: {cds})", "critico"))

    ibov_var = _get(ind, "ibovespa", "variacao_dia")
    if ibov_var is not None:
        limite = -abs(cfg.get("queda_ibovespa_dia_pct", 5.0))
        regras.append(("queda_ibovespa", ibov_var <= limite,
                        f"🚨 Queda do Ibovespa superior a {abs(limite)}% no dia (atual: {ibov_var:.2f}%)", "critico"))

    ativos = []
    for chave, condicao, mensagem, nivel in regras:
        if condicao:
            db.registrar_alerta(chave, mensagem, nivel)
            ativos.append({"chave": chave, "mensagem": mensagem, "nivel": nivel})
        else:
            db.resolver_alerta(chave)

    return ativos


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(avaliar(), ensure_ascii=False, indent=2))
