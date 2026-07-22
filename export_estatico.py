#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera um snapshot ESTÁTICO e visualmente idêntico ao painel local, para
publicar no GitHub Pages (que só serve arquivo estático — não roda o
backend Flask). Roda a atualização de indicadores primeiro, monta o mesmo
payload da API (/api/dados) e embute o JSON direto no HTML.

Saída (na raiz do projeto, pronta pra virar a home do GitHub Pages):
  index.html
  css/style.css
  js/dashboard.js
  images/logo_netway.png
"""

import json
import os
import shutil
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from database import db  # noqa: E402
from app.api.routes import atualizar_tudo, montar_payload  # noqa: E402

TEMPLATE_PATH = os.path.join(BASE_DIR, "export", "template_estatico.html")


def exportar(atualizar_antes=True):
    db.init_db()
    if atualizar_antes:
        print("[export_estatico] atualizando indicadores antes de exportar...")
        try:
            atualizar_tudo()
        except Exception as e:
            print(f"[export_estatico] atualização teve falhas parciais: {e}")

    payload = montar_payload()
    payload["gerado_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    html = template.replace("__DADOS_JSON__", json.dumps(payload, ensure_ascii=False))
    html = html.replace("__GERADO_EM__", payload["gerado_em"])

    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    dest_css = os.path.join(BASE_DIR, "css")
    dest_js = os.path.join(BASE_DIR, "js")
    dest_img = os.path.join(BASE_DIR, "images")
    os.makedirs(dest_css, exist_ok=True)
    os.makedirs(dest_js, exist_ok=True)
    os.makedirs(dest_img, exist_ok=True)

    shutil.copy(os.path.join(BASE_DIR, "app", "dashboard", "static", "css", "style.css"), os.path.join(dest_css, "style.css"))
    shutil.copy(os.path.join(BASE_DIR, "app", "dashboard", "static", "js", "dashboard.js"), os.path.join(dest_js, "dashboard.js"))
    shutil.copy(os.path.join(BASE_DIR, "app", "dashboard", "static", "js", "plotly.min.js"), os.path.join(dest_js, "plotly.min.js"))
    shutil.copy(os.path.join(BASE_DIR, "app", "dashboard", "static", "images", "logo_netway.png"), os.path.join(dest_img, "logo_netway.png"))

    print(f"[export_estatico] snapshot gerado em {payload['gerado_em']} — index.html + css/ + js/ + images/ na raiz do projeto.")


if __name__ == "__main__":
    exportar()
