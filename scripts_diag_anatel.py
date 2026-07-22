#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de diagnóstico TEMPORÁRIO — descobre a URL real dos arquivos de
dados abertos da Anatel (acessos de banda larga fixa por operadora/UF).
Roda dentro do GitHub Actions (internet real) e grava tudo em
debug_anatel.log pra eu conseguir ler via raw.githubusercontent.com.
Apagar este arquivo depois de descobrir a URL certa."""
import sys
import os
import urllib.request
import ssl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from services._http import abrir_url  # noqa: E402

LOG = []


def log(msg):
    print(msg)
    LOG.append(msg)


def tentar(url):
    try:
        with abrir_url(url, timeout=15) as resp:
            corpo = resp.read()
            log(f"OK ({len(corpo)} bytes) — {url}")
            return corpo
    except Exception as e:
        log(f"FALHOU ({type(e).__name__}: {e}) — {url}")
        return None


log("=== Baixando Inventario_de_Bases_de_Dados.csv ===")
inventario = tentar("https://www.anatel.gov.br/dadosabertos/PDA/Bases_Publicadas/Inventario_de_Bases_de_Dados.csv")
if inventario:
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            texto = inventario.decode(enc)
            log(f"--- decodificado como {enc}, {len(texto)} chars ---")
            break
        except UnicodeDecodeError:
            continue
    else:
        texto = inventario.decode("latin-1", errors="replace")

    linhas = texto.splitlines()
    log(f"total de linhas: {len(linhas)}")
    log("--- primeiras 3 linhas (cabeçalho) ---")
    for l in linhas[:3]:
        log(l)
    log("--- linhas contendo SCM / Banda Larga / Municipio / UF (até 40) ---")
    achados = [l for l in linhas if any(k in l for k in ["SCM", "Banda Larga", "BANDA LARGA", "banda larga", "Município", "Municipio", "scm"])]
    for l in achados[:40]:
        log(l)
    log(f"total de linhas relevantes encontradas: {len(achados)}")

log("=== Testando candidatos diretos na pasta SCM ===")
candidatos = [
    "Total.csv", "total.csv", "TOTAL.csv",
    "Empresa.csv", "Grupo.csv", "Municipio.csv", "UF.csv", "Regiao.csv", "Tecnologia.csv",
    "Acessos_Banda_Larga_Fixa.csv", "Acessos_SCM.csv", "SCM.csv",
    "Acessos_Banda_Larga_Fixa_Municipio.csv", "Acessos_Banda_Larga_Fixa_UF.csv",
    "Acessos_Banda_Larga_Fixa_Empresa.csv", "Acessos_Banda_Larga_Fixa_Grupo.csv",
]
for nome in candidatos:
    tentar(f"https://www.anatel.gov.br/dadosabertos/PDA/Acessos/SCM/{nome}")

log("=== Achado no inventario: dataset real é 'dados-de-acessos-de-comunicacao-multimidia' ===")
log("=== Testando API CKAN do dados.gov.br com o slug certo ===")
pkg = tentar("https://dados.gov.br/api/3/action/package_show?id=dados-de-acessos-de-comunicacao-multimidia")
if pkg:
    for enc in ("utf-8", "latin-1"):
        try:
            log(pkg.decode(enc)[:4000])
            break
        except UnicodeDecodeError:
            continue

log("=== Testando subdominio informacoes.anatel.gov.br (onde o painel realmente mora) ===")
for nome in ["Total.csv", "Municipio.csv", "UF.csv", "Empresa.csv", "Grupo.csv"]:
    tentar(f"https://informacoes.anatel.gov.br/dadosabertos/PDA/Acessos/SCM/{nome}")

with open("debug_anatel.log", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))

print("\n\n[diagnostico] gravado em debug_anatel.log")
