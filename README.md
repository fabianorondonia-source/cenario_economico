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

Se a porta já estava em uso por uma execução anterior (ou pelo painel
antigo), `start.command` encerra o processo velho e sobe a versão atual —
assim nunca fica preso mostrando código desatualizado.

## Onde ver o log

Toda execução de `start.command`, `Publicar_no_GitHub.command` ou da
automação diária grava (e acrescenta) em **`atualizacao.log`**, na raiz
desta pasta — sempre o mesmo arquivo, não importa qual dos três você rodou.
Abra esse arquivo num editor de texto qualquer para ver se cada indicador
buscou dado com sucesso ("— OK") ou falhou (com o motivo do erro).

## Arquitetura

```
app/            → Flask (rotas da API + template + CSS/JS do dashboard)
services/
  economy/      → Banco Central (SGS): PIB-proxy, IPCA, IGP-M, Selic, desemprego,
                  dívida pública, resultado fiscal, produção industrial, varejo
  indicators/   → mercado financeiro (Yahoo Finance, CoinGecko) + risco-país/rating (manual)
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
| Ibovespa, S&P 500, Nasdaq, Dow Jones, ouro, petróleo, VIX | Yahoo Finance | Sim |
| Bitcoin | CoinGecko | Sim |
| Ações de grupos telecom de capital aberto (Brisanet, Unifique, American Tower, IHS Holding) | Yahoo Finance | Sim |
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

## Atualização automática diária

Há **duas** camadas de automação — pode usar as duas juntas, elas não
conflitam (a segunda commitada sempre vence a mais antiga):

### 1. GitHub Actions (recomendado — roda sozinho, mesmo com o Mac desligado)

`.github/workflows/atualizar.yml` roda todo dia às **7h (horário de
Brasília)** direto na infraestrutura do GitHub: baixa o repositório, instala
as dependências, roda `export_estatico.py` (que busca os dados reais na
internet — Banco Central, stooq.com, CoinGecko) e publica o snapshot
atualizado sozinho, sem depender do Mac do Fabiano estar ligado, de internet
local, ou de nenhum script rodar na máquina. Também dá pra disparar na hora
pela aba **Actions** do repositório no GitHub (botão "Run workflow"), sem
precisar esperar o dia seguinte.

### 2. launchd no Mac (opcional — mantém o painel local também sincronizado)

Duplo clique **uma única vez** em `Instalar_Atualizacao_Automatica.command`.
Isso liga um agendamento (launchd) que todo dia às 7h roda
`atualizar_e_publicar.sh` sozinho: atualiza todos os indicadores automáticos
e republica o snapshot no GitHub — sem você precisar abrir `start.command`
nem `Publicar_no_GitHub.command`. Útil porque também atualiza o
`database/dashboard.db` local (cache usado pelo painel rodando via
`start.command`). Para desativar: `launchctl unload ~/Library/LaunchAgents/com.netway.economicintelligencedashboard.plist`.

O histórico dos scores (`database/historico_scores.json`) é versionado no
git — por isso sobrevive tanto às execuções efêmeras do GitHub Actions
quanto a reinstalações do projeto.

## Adicionando um novo indicador

1. Adicione a série/fonte em `services/<módulo>/*.py`, chamando
   `db.upsert_indicador(...)`.
2. Se quiser que ele entre em algum score, edite
   `services/scoring/investment_score.py` ou `ma_score.py`.
3. Adicione o card correspondente em `app/dashboard/static/js/dashboard.js`
   (função `renderKpis`).
