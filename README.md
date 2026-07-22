# Economic Intelligence Dashboard — Grupo Netway

Painel executivo de inteligência econômica para apoiar decisões estratégicas
do Grupo Netway: como está a economia brasileira, o mercado financeiro, o
crédito e o setor de provedores regionais (ISPs) — com dois índices centrais:

- **Momento de Investimento** (0-100): cenário macro geral favorece investir/expandir?
- **M&A Score** (0-100, 🟢🟡🟠🔴): é bom momento para adquirir provedores regionais?

Este painel é uma **ferramenta de apoio analítico**. Não constitui
recomendação de investimento, jurídica ou financeira — decisões de aquisição
exigem due diligence completa e assessoria especializada.

## Como rodar

```
duplo clique em start.command   (macOS)
./start.sh                       (Linux)
```

Isso cria um ambiente virtual, instala as dependências (`requirements.txt`),
roda a primeira atualização de indicadores e sobe o servidor em
`http://localhost:8750` (porta configurável em `config/settings.json`).

## Arquitetura

```
app/            → Flask (rotas da API + template + CSS/JS do dashboard)
services/
  economy/      → Banco Central (SGS): PIB-proxy, IPCA, IGP-M, Selic, desemprego,
                  dívida pública, resultado fiscal, produção industrial, varejo
  indicators/   → mercado financeiro (stooq.com, CoinGecko) + risco-país/rating (manual)
  telecom/      → setor de ISPs (múltiplos, participação, M&A) + grandes grupos
  scoring/      → Momento de Investimento e M&A Score (regras determinísticas)
  narrative/    → gerador de insights em texto (regras if/then, sem IA generativa)
  alerts/       → motor de alertas por threshold (config/settings.json)
database/       → SQLite: cache de indicadores + histórico dos scores + log de alertas
config/         → settings.json (porta, intervalo de atualização, thresholds de alerta)
github/         → script de publicação no GitHub
```

## Fontes de dados

Só fontes **gratuitas e sem necessidade de cadastro/chave de API**:

| Indicador | Fonte | Automático? |
|---|---|---|
| Selic, IPCA, IGP-M, desemprego, dívida pública, resultado fiscal, produção industrial, varejo, spread bancário, taxa de crédito, inadimplência | Banco Central (SGS) | Sim |
| Dólar, Euro | Banco Central (SGS — PTAX) | Sim |
| Ibovespa, S&P 500, Nasdaq, Dow Jones, ouro, petróleo, VIX | stooq.com | Sim |
| Bitcoin | CoinGecko | Sim |
| Ações de grupos telecom de capital aberto (Brisanet, Unifique, American Tower, IHS Holding) | stooq.com | Sim |
| Risco-país (CDS), rating soberano, projeções de PIB/IPCA | Curadoria manual — sem API pública (EMBI+ foi descontinuado em 2024) | Não |
| Múltiplos de M&A, participação de mercado, churn, movimentações, riscos regulatórios do setor de ISPs | Curadoria manual — sem API pública para dados de M&A do setor | Não |
| Grupos de capital fechado (Desktop, Vero, Ligga, Mhnet, Brasil Tecpar, Algar, V.tal, Fibrasil, Neutral Networks) | Perfil curado — sem dado público de mercado | Não |

Indicadores automáticos são marcados `"atualizacao": "automatica"` no banco;
os manuais, `"manual"`. A interface mostra uma etiqueta "manual" em cada
cartão que depende de curadoria.

## Atualização automática

O intervalo é configurável em `config/settings.json` (`intervalo_atualizacao_minutos`,
padrão 60) ou via `POST /api/config`. Um agendador (APScheduler) roda em
background enquanto o servidor está de pé. Há também um botão "Atualizar
agora" na interface, que chama `POST /api/atualizar`.

## Publicar no GitHub

`Publicar_no_GitHub.command` (na raiz do projeto) roda `export_estatico.py` (gera um
snapshot visual — `index.html` + `css/` + `js/` + `images/` na raiz, com os
dados do momento embutidos) e publica tudo no repositório
`fabianorondonia-source/cenario_economico`. **Importante:** GitHub Pages só
serve arquivo estático — o backend Flask (API, banco SQLite, agendador) não
roda lá. Por isso o link público (https://fabianorondonia-source.github.io/cenario_economico/)
mostra uma "foto" do painel no momento da última publicação — com a mesma
cara profissional do painel local — enquanto o painel com dados ao vivo e
atualização automática só funciona rodando localmente via
`start.command`/`start.sh`. Rode `Publicar_no_GitHub.command` sempre
que quiser atualizar o snapshot público (por exemplo, antes de uma reunião).

## Atualização automática diária (sem precisar abrir nada)

Duplo clique **uma única vez** em `Instalar_Atualizacao_Automatica.command`.
Isso liga um agendamento (launchd) que todo dia às 7h roda
`atualizar_e_publicar.sh` sozinho: atualiza todos os indicadores automáticos
e republica o snapshot no GitHub — sem você precisar abrir `start.command`
nem `Publicar_no_GitHub.command`. Log de cada execução em `auto_update.log`.
Para desativar: `launchctl unload ~/Library/LaunchAgents/com.netway.economicintelligencedashboard.plist`.

## Adicionando um novo indicador

1. Adicione a série/fonte em `services/<módulo>/*.py`, chamando
   `db.upsert_indicador(...)`.
2. Se quiser que ele entre em algum score, edite
   `services/scoring/investment_score.py` ou `ma_score.py`.
3. Adicione o card correspondente em `app/dashboard/static/js/dashboard.js`
   (função `renderKpis`).
