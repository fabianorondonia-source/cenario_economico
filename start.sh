#!/bin/bash
# Economic Intelligence Dashboard — Grupo Netway (Linux/genérico)
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

PYTHON=python3
if [ -d ".venv" ]; then
  source .venv/bin/activate
else
  echo "Criando ambiente virtual (.venv)..."
  $PYTHON -m venv .venv
  source .venv/bin/activate
fi

echo "Instalando/checando dependências..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

python3 startup.py
