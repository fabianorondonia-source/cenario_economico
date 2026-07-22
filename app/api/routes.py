"""
Rotas da API do Economic Intelligence Dashboard (Grupo Netway).

GET  /api/dados         -> payload consolidado (economia, mercado, crédito,
                            telecom, scores, insights, alertas)
GET  /api/historico/<chave> -> série histórica de um indicador (para gráficos)
POST /api/atualizar     -> força atualização de todos os indicadores agora
GET  /api/config        -> configurações atuais (porta, intervalo, alertas)
POST /api/config        -> atualiza intervalo de atualização (minutos)
"""

import json
import os
import sys
from flask import Blueprint, jsonify, request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from database import db  # noqa: E402
from services.economy import bcb  # noqa: E402
from services.indicators import markets, risk  # noqa: E402
from services.telecom import sector, players, ranking  # noqa: E402
from services.scoring import investment_score, ma_score  # noqa: E402
from services.narrative import generator as narrative_generator  # noqa: E402
from services.alerts import engine as alerts_engine  # noqa: E402

api_bp = Blueprint("api", __name__, url_prefix="/api")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "settings.json")


def carregar_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def atualizar_tudo():
    """Roda todos os fetchers, recalcula scores, avalia alertas e grava
    um snapshot histórico dos scores. Chamada no boot, pelo agendador
    periódico e pelo endpoint /api/atualizar."""
    print("[atualizar_tudo] iniciando ciclo de atualização...")
    for modulo, nome in [
        (bcb.atualizar_todos, "economia/crédito (BCB)"),
        (markets.atualizar_todos, "mercado financeiro"),
        (risk.atualizar_todos, "risco-país/rating (manual)"),
        (sector.atualizar_todos, "setor de provedores (manual)"),
        (players.atualizar_todos, "grandes grupos telecom"),
        (ranking.atualizar_todos, "ranking de provedores (manual)"),
    ]:
        try:
            modulo()
        except Exception as e:
            print(f"[atualizar_tudo] módulo '{nome}' falhou por completo: {e}")

    inv = investment_score.calcular()
    ma = ma_score.calcular()
    if inv.get("score") is not None and ma.get("score") is not None:
        db.insert_score_snapshot(inv["score"], ma["score"])

    alertas_engine_result = alerts_engine.avaliar()
    print(f"[atualizar_tudo] ciclo concluído. {len(alertas_engine_result)} alerta(s) ativo(s).")
    return {"investimento": inv, "ma_score": ma, "alertas": alertas_engine_result}


def montar_payload():
    """Consolida tudo que o dashboard precisa num único dict — usado pela
    rota /api/dados E pelo export_estatico.py (snapshot pro GitHub Pages),
    pra nunca haver duas versões da mesma lógica divergindo."""
    ind = db.get_todos_indicadores()
    inv = investment_score.calcular()
    ma = ma_score.calcular()
    insights = narrative_generator.gerar_insights()
    alertas_ativos = db.get_alertas_ativos()
    historico_scores = db.get_score_history()

    def bloco(categoria):
        return {k: v for k, v in ind.items() if v.get("categoria") == categoria}

    return {
        "economia": bloco("economia"),
        "mercado": bloco("mercado"),
        "credito": bloco("credito"),
        "risco": bloco("risco"),
        "telecom_setor": bloco("telecom_setor"),
        "telecom_grupos": bloco("telecom_grupos"),
        "telecom_ranking": bloco("telecom_ranking"),
        "scores": {"momento_investimento": inv, "ma_score": ma},
        "historico_scores": historico_scores,
        "insights": insights,
        "alertas": alertas_ativos,
        "disclaimer": (
            "Painel de apoio analítico com dados públicos e curadoria manual. "
            "Não constitui recomendação de investimento, jurídica ou financeira. "
            "Decisões de aquisição exigem due diligence completa e assessoria especializada."
        ),
    }


@api_bp.route("/dados", methods=["GET"])
def dados():
    return jsonify(montar_payload())


@api_bp.route("/historico/<chave>", methods=["GET"])
def historico(chave):
    ind = db.get_indicador(chave)
    if not ind:
        return jsonify({"erro": "indicador não encontrado"}), 404
    return jsonify(ind)


@api_bp.route("/atualizar", methods=["POST"])
def atualizar():
    resultado = atualizar_tudo()
    return jsonify({"ok": True, "resultado": resultado})


@api_bp.route("/config", methods=["GET"])
def get_config():
    return jsonify(carregar_config())


@api_bp.route("/config", methods=["POST"])
def set_config():
    payload = request.get_json(force=True, silent=True) or {}
    cfg = carregar_config()
    if "intervalo_atualizacao_minutos" in payload:
        try:
            cfg["intervalo_atualizacao_minutos"] = max(5, int(payload["intervalo_atualizacao_minutos"]))
        except (ValueError, TypeError):
            pass
    salvar_config(cfg)
    return jsonify(cfg)
