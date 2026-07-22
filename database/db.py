"""
Camada de persistência (SQLite) do Economic Intelligence Dashboard.

Guarda:
  - cache_indicadores: último valor bom conhecido de cada indicador (para a
    dashboard nunca ficar "em branco" se uma API gratuita cair).
  - historico_scores: série histórica dos scores que NÓS calculamos
    (Momento de Investimento, M&A Score) — não existe fonte externa pra isso.
  - alertas_log: registro de quando cada alerta de threshold ligou/desligou.
"""

import json
import os
import sqlite3
import time
from datetime import datetime, timezone

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "dashboard.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")

# Esta pasta vive dentro de uma pasta sincronizada por iCloud/Obsidian. SQLite
# usa locks de arquivo que podem colidir com o processo de sincronização —
# journal_mode=DELETE (mais simples que WAL, que cria arquivos extras -wal/-shm
# que também precisariam sincronizar) + busy_timeout reduzem bastante o risco
# de "database is locked" / "disk I/O error" transitório.
_RETRIES = 3


def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=DELETE;")
    conn.execute("PRAGMA busy_timeout=8000;")
    return conn


def _com_retry(func, *args, **kwargs):
    ultimo_erro = None
    for tentativa in range(_RETRIES):
        try:
            return func(*args, **kwargs)
        except sqlite3.OperationalError as e:
            ultimo_erro = e
            time.sleep(0.5 * (tentativa + 1))
    raise ultimo_erro


def init_db():
    conn = get_conn()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def _agora():
    return datetime.now(timezone.utc).astimezone().strftime("%d/%m/%Y %H:%M:%S")


def upsert_indicador(chave, categoria=None, valor=None, unidade=None,
                      data_referencia=None, variacao_dia=None, fonte=None,
                      atualizacao="automatica", historico=None):
    """Insere ou atualiza um indicador. Se `valor` vier None, mantém o valor
    anterior em cache (não sobrescreve um bom dado com um vazio)."""
    conn = get_conn()
    cur = conn.cursor()
    existente = cur.execute(
        "SELECT * FROM cache_indicadores WHERE chave = ?", (chave,)
    ).fetchone()

    if valor is None and existente is not None:
        valor = existente["valor"]
        data_referencia = data_referencia or existente["data_referencia"]
        variacao_dia = variacao_dia if variacao_dia is not None else existente["variacao_dia"]

    hist_json = json.dumps(historico, ensure_ascii=False) if historico is not None else (
        existente["historico_json"] if existente else None
    )

    cur.execute("""
        INSERT INTO cache_indicadores
            (chave, categoria, valor, unidade, data_referencia, variacao_dia, fonte, atualizacao, historico_json, atualizado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(chave) DO UPDATE SET
            categoria = excluded.categoria,
            valor = excluded.valor,
            unidade = excluded.unidade,
            data_referencia = excluded.data_referencia,
            variacao_dia = excluded.variacao_dia,
            fonte = excluded.fonte,
            atualizacao = excluded.atualizacao,
            historico_json = excluded.historico_json,
            atualizado_em = excluded.atualizado_em
    """, (chave, categoria, valor, unidade, data_referencia, variacao_dia, fonte,
          atualizacao, hist_json, _agora()))
    conn.commit()
    conn.close()


def get_indicador(chave):
    conn = get_conn()
    row = conn.execute("SELECT * FROM cache_indicadores WHERE chave = ?", (chave,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["historico"] = json.loads(d.pop("historico_json") or "[]")
    return d


def get_indicadores_por_categoria(categoria):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM cache_indicadores WHERE categoria = ? ORDER BY chave", (categoria,)
    ).fetchall()
    conn.close()
    out = []
    for row in rows:
        d = dict(row)
        d["historico"] = json.loads(d.pop("historico_json") or "[]")
        out.append(d)
    return out


def get_todos_indicadores():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM cache_indicadores").fetchall()
    conn.close()
    out = {}
    for row in rows:
        d = dict(row)
        d["historico"] = json.loads(d.pop("historico_json") or "[]")
        out[d["chave"]] = d
    return out


def insert_score_snapshot(momento_investimento, ma_score):
    conn = get_conn()
    conn.execute(
        "INSERT INTO historico_scores (data, momento_investimento, ma_score, criado_em) VALUES (?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d"), momento_investimento, ma_score, _agora())
    )
    conn.commit()
    conn.close()


def get_score_history(limite=90):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM historico_scores ORDER BY id DESC LIMIT ?", (limite,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


def registrar_alerta(chave, mensagem, nivel="atencao"):
    """Só grava uma nova linha se o alerta não estiver ativo ainda (evita log duplicado a cada refresh)."""
    conn = get_conn()
    ja_ativo = conn.execute(
        "SELECT id FROM alertas_log WHERE chave = ? AND ativo = 1", (chave,)
    ).fetchone()
    if not ja_ativo:
        conn.execute(
            "INSERT INTO alertas_log (chave, mensagem, nivel, ativo, criado_em) VALUES (?, ?, ?, 1, ?)",
            (chave, mensagem, nivel, _agora())
        )
        conn.commit()
    conn.close()


def resolver_alerta(chave):
    conn = get_conn()
    conn.execute(
        "UPDATE alertas_log SET ativo = 0, resolvido_em = ? WHERE chave = ? AND ativo = 1",
        (_agora(), chave)
    )
    conn.commit()
    conn.close()


def get_alertas_ativos():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM alertas_log WHERE ativo = 1 ORDER BY criado_em DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
