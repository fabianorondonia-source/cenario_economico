#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ponto de entrada do Economic Intelligence Dashboard (Grupo Netway).

1. Garante que o banco SQLite existe (cria as tabelas se necessário).
2. Roda um primeiro ciclo de atualização de todos os indicadores.
3. Sobe o agendador em background (intervalo configurável em config/settings.json).
4. Inicia o servidor Flask.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db
from app import create_app, iniciar_agendador
from app.api.routes import atualizar_tudo, carregar_config


def main():
    print("=== Economic Intelligence Dashboard — Grupo Netway ===")
    db.init_db()
    print("[startup] banco de dados OK.")

    print("[startup] rodando primeira atualização de indicadores...")
    try:
        atualizar_tudo()
    except Exception as e:
        print(f"[startup] atualização inicial teve falhas parciais: {e}")

    app = create_app()
    iniciar_agendador(app)

    cfg = carregar_config()
    porta = cfg.get("porta", 8750)
    print(f"[startup] servidor em http://localhost:{porta}")
    app.run(host="0.0.0.0", port=porta, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
