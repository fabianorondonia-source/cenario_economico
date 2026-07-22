#!/bin/bash
# Roda sozinho todo dia (via launchd) — atualiza todos os indicadores,
# gera o snapshot estático e publica no GitHub. Equivalente automático do
# duplo clique em Publicar_no_GitHub.command.
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

DIR="/Users/fabiano/Library/Mobile Documents/iCloud~md~obsidian/Documents/Fabiano IA/Netway/Economic Intelligence Dashboard"
cd "$DIR" || exit 1
LOG="$DIR/auto_update.log"

echo "=== $(date '+%d/%m/%Y %H:%M') ===" >> "$LOG"

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

python3 export_estatico.py >> "$LOG" 2>&1

rm -f .git/index.lock 2>/dev/null

if [ ! -d .git ] || ! git remote get-url origin >/dev/null 2>&1; then
  echo "Repositório git ainda não configurado — rode Publicar_no_GitHub.command manualmente uma vez primeiro." >> "$LOG"
  exit 1
fi

git add -A >> "$LOG" 2>&1
if git commit -m "Atualização automática — $(date '+%d/%m/%Y %H:%M')" >> "$LOG" 2>&1; then
  git push origin main >> "$LOG" 2>&1
else
  echo "Nada novo para publicar." >> "$LOG"
fi
echo "" >> "$LOG"
