const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

// Paleta alinhada ao style.css (mesmos tons usados nas variáveis --accent,
// --verde, --amarelo, --vermelho, --texto, --texto-sec).
const COR = {
  accent: '#7c6cf0',
  accent2: '#a99bff',
  accentSoft: 'rgba(124,108,240,0.18)',
  verde: '#22c55e',
  amarelo: '#f2b544',
  vermelho: '#ef4a63',
  texto: '#eef0f5',
  textoSec: '#8791a8',
};

const PLOTLY_DARK = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { color: COR.texto, size: 11, family: '-apple-system, "Segoe UI", Roboto, sans-serif' },
  margin: { t: 34, l: 44, r: 20, b: 34 },
};
const PLOTLY_CONFIG = { displayModeBar: false, responsive: true };
const TEM_PLOTLY = typeof Plotly !== 'undefined';

let dados = null;

function plotlySeguro(elId, data, layout, config) {
  if (!TEM_PLOTLY) {
    const el = document.getElementById(elId);
    if (el) el.innerHTML = '<div style="text-align:center;color:var(--texto-sec);padding-top:60px;font-size:.78rem">gráfico indisponível (Plotly não carregou — verifique a internet)</div>';
    return;
  }
  try {
    Plotly.newPlot(elId, data, layout, config);
  } catch (e) {
    console.warn(`falha ao desenhar gráfico ${elId}`, e);
    graficoVazio(elId, 'não foi possível desenhar este gráfico com os dados atuais');
  }
}

// Em vez de deixar o Plotly desenhar um grid vazio (0-4, -1-6) quando não
// há pontos suficientes — o que fica parecendo erro/bug — mostra uma
// mensagem clara. Isso acontece tipicamente quando o painel ainda não
// rodou nenhuma atualização com internet real (ex.: logo após publicar).
function graficoVazio(elId, msg) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:100%;min-height:180px;text-align:center;color:var(--texto-sec);font-size:.78rem;padding:0 20px;line-height:1.5">Sem dados suficientes ainda —<br>${esc(msg)}.</div>`;
}

function fmtNum(v, casas = 2) {
  if (v === null || v === undefined || isNaN(v)) return '—';
  return Number(v).toLocaleString('pt-BR', { minimumFractionDigits: casas, maximumFractionDigits: casas });
}

function classeAlerta(nota) {
  if (nota >= 70) return 'verde';
  if (nota >= 45) return 'amarelo';
  return 'vermelho';
}

function tagManual(item) {
  return (item && item.atualizacao === 'manual') ? '<span class="manual">manual</span>' : '';
}

async function carregar() {
  try {
    const r = await fetch('/api/dados?t=' + Date.now(), { cache: 'no-store' });
    if (!r.ok) return;
    dados = await r.json();
    render();
  } catch (e) { console.warn('falha ao carregar /api/dados', e); }
}

async function atualizarAgora() {
  const btn = document.getElementById('btn-atualizar');
  btn.disabled = true;
  btn.textContent = 'Atualizando…';
  try {
    await fetch('/api/atualizar', { method: 'POST' });
    await carregar();
  } finally {
    btn.disabled = false;
    btn.textContent = 'Atualizar agora';
  }
}

function relogio() {
  document.getElementById('relogio').textContent = new Date().toLocaleString('pt-BR');
}

// ===== Faixa de mercado (chips estáticos, sem marquee) =====
function renderTicker() {
  if (!dados) return;
  const itens = [];
  const add = (label, item, casas = 2, prefixo = '') => {
    if (!item || item.valor === null || item.valor === undefined) return;
    const v = prefixo + fmtNum(item.valor, casas);
    const varr = item.variacao_dia;
    const seta = varr == null ? '' : (varr >= 0 ? `<span class="up">▲${fmtNum(Math.abs(varr),2)}%</span>` : `<span class="down">▼${fmtNum(Math.abs(varr),2)}%</span>`);
    itens.push(`<span class="ticker-item"><span class="lbl">${label}</span><span class="val">${v}</span>${seta}</span>`);
  };
  add('USD/BRL', dados.mercado.dolar_ptax, 4, 'R$ ');
  add('EUR/BRL', dados.mercado.euro_ptax, 4, 'R$ ');
  add('IBOVESPA', dados.mercado.ibovespa, 0);
  add('S&P500', dados.mercado.sp500, 0);
  add('NASDAQ', dados.mercado.nasdaq, 0);
  add('DOW JONES', dados.mercado.dow_jones, 0);
  add('OURO', dados.mercado.ouro, 2, 'US$ ');
  add('PETRÓLEO', dados.mercado.petroleo, 2, 'US$ ');
  add('BITCOIN', dados.mercado.bitcoin, 0, 'US$ ');
  add('VIX', dados.mercado.vix, 2);
  add('SELIC', dados.economia.selic_meta, 2, '');
  add('IPCA 12M', dados.economia.ipca_12m, 2, '');
  document.getElementById('ticker-track').innerHTML = itens.join(' &nbsp;·&nbsp; ') || 'Sem dados no momento.';
}

// ===== KPIs genéricos =====
function kpiHtml(titulo, item, casas, unidadeTxt, prefixo) {
  if (!item) return '';
  const nota = item.variacao_dia == null ? 60 : Math.abs(item.variacao_dia) < 1 ? 70 : 40;
  const varr = item.variacao_dia;
  const valorTxt = item.valor !== null && item.valor !== undefined
    ? `${prefixo || ''}${fmtNum(item.valor, casas)}<span class="un">${unidadeTxt ? ' ' + unidadeTxt : ''}</span>`
    : 'sem dado';
  return `
    <div class="kpi ${classeAlerta(nota)}">
      <div class="t"><span>${esc(titulo)}</span>${tagManual(item)}</div>
      <div class="v">${valorTxt}${varr != null ? `<span class="var ${varr >= 0 ? 'up' : 'down'}">${varr >= 0 ? '▲' : '▼'} ${fmtNum(Math.abs(varr))}%</span>` : ''}</div>
      <div class="fonte">${esc(item.fonte || '')} ${item.data_referencia ? '· ' + esc(item.data_referencia) : ''}</div>
    </div>`;
}

function renderKpis() {
  const e = dados.economia, m = dados.mercado, c = dados.credito, ri = dados.risco;

  document.getElementById('kpis-economia').innerHTML = [
    kpiHtml('Selic (meta)', e.selic_meta, 2, '% a.a.'),
    kpiHtml('IPCA (mensal)', e.ipca_mensal, 2, '%'),
    kpiHtml('IPCA (12 meses)', e.ipca_12m, 2, '%'),
    kpiHtml('IGP-M (mensal)', e.igpm_mensal, 2, '%'),
    kpiHtml('Desemprego', e.desemprego, 1, '%'),
    kpiHtml('Dívida Bruta/PIB', e.divida_bruta_pib, 1, '% PIB'),
    kpiHtml('Resultado Primário', e.resultado_primario, 0, 'R$ mi'),
    kpiHtml('Produção Industrial', e.producao_industrial, 1, 'índice'),
    kpiHtml('Vendas no Varejo', e.vendas_varejo, 1, 'índice'),
    kpiHtml('Risco-país (CDS)', ri.risco_pais_cds, 0, 'pts'),
  ].join('');
  // PIB/IPCA projeção como card textual (min-max)
  if (ri.pib_projecao_min && ri.pib_projecao_max) {
    document.getElementById('kpis-economia').innerHTML += `
      <div class="kpi">
        <div class="t"><span>PIB — projeção 2026</span><span class="manual">manual</span></div>
        <div class="v">${ri.pib_projecao_min.valor}–${ri.pib_projecao_max.valor}<span class="un">%</span></div>
        <div class="fonte">${esc(ri.pib_projecao_min.fonte)}</div>
      </div>`;
  }
  if (ri.ipca_projecao_min && ri.ipca_projecao_max) {
    document.getElementById('kpis-economia').innerHTML += `
      <div class="kpi">
        <div class="t"><span>IPCA — projeção 2026</span><span class="manual">manual</span></div>
        <div class="v">${ri.ipca_projecao_min.valor}–${ri.ipca_projecao_max.valor}<span class="un">%</span></div>
        <div class="fonte">${esc(ri.ipca_projecao_min.fonte)}</div>
      </div>`;
  }

  document.getElementById('kpis-mercado').innerHTML = [
    kpiHtml('Dólar (PTAX)', m.dolar_ptax, 4, '', 'R$ '),
    kpiHtml('Euro (PTAX)', m.euro_ptax, 4, '', 'R$ '),
    kpiHtml('Ibovespa', m.ibovespa, 0, 'pts'),
    kpiHtml('S&P 500', m.sp500, 0, 'pts'),
    kpiHtml('Nasdaq', m.nasdaq, 0, 'pts'),
    kpiHtml('Dow Jones', m.dow_jones, 0, 'pts'),
    kpiHtml('Ouro', m.ouro, 2, '', 'US$ '),
    kpiHtml('Petróleo (WTI)', m.petroleo, 2, '', 'US$ '),
    kpiHtml('Bitcoin', m.bitcoin, 0, '', 'US$ '),
    kpiHtml('Volatilidade (VIX)', m.vix, 2, 'pts'),
  ].join('');
  if (ri.rating_sp) {
    document.getElementById('kpis-mercado').innerHTML += `
      <div class="kpi">
        <div class="t"><span>Rating soberano</span><span class="manual">manual</span></div>
        <div class="v" style="font-size:1rem">S&amp;P ${ri.rating_sp.historico?.[0]?.valor_texto || '—'} · Moody's ${ri.rating_moodys?.historico?.[0]?.valor_texto || '—'} · Fitch ${ri.rating_fitch?.historico?.[0]?.valor_texto || '—'}</div>
        <div class="fonte">${esc(ri.rating_sp.fonte)}</div>
      </div>`;
  }

  document.getElementById('kpis-credito').innerHTML = [
    kpiHtml('Spread Bancário', c.spread_bancario, 1, 'p.p.'),
    kpiHtml('Taxa Média de Crédito', c.taxa_media_credito, 1, '% a.a.'),
    kpiHtml('Inadimplência', c.inadimplencia, 2, '%'),
  ].join('');

  const t = dados.telecom_setor;
  document.getElementById('kpis-telecom').innerHTML = [
    (t.multiplo_ev_ebitda_atual ? `
      <div class="kpi">
        <div class="t"><span>Múltiplo EV/EBITDA</span><span class="manual">manual</span></div>
        <div class="v"><span style="text-decoration:line-through;color:var(--texto-sec);font-size:.9rem">${t.multiplo_ev_ebitda_2021.valor}x</span> → ${t.multiplo_ev_ebitda_atual.valor}x</div>
        <div class="fonte">${esc(t.multiplo_ev_ebitda_atual.fonte)}</div>
      </div>` : ''),
    kpiHtml('Participação ISPs (banda larga)', t.participacao_isps_banda_larga, 1, '%'),
    kpiHtml('Crescimento assinantes (24-25)', t.crescimento_assinantes_2024_2025, 1, '%'),
    kpiHtml('Crescimento assinantes (18-25)', t.crescimento_assinantes_2018_2025, 0, '%'),
    (t.churn_setorial_min ? `
      <div class="kpi">
        <div class="t"><span>Churn setorial</span><span class="manual">manual</span></div>
        <div class="v">${t.churn_setorial_min.valor}–${t.churn_setorial_max.valor}<span class="un">% a.a.</span></div>
        <div class="fonte">${esc(t.churn_setorial_min.fonte)}</div>
      </div>` : ''),
  ].join('');
}

// ===== Scores (gauges) =====
function renderGauge(elId, valor, titulo, cor) {
  if (valor === null || valor === undefined) {
    document.getElementById(elId).innerHTML = '<div style="text-align:center;color:var(--texto-sec);padding-top:60px">sem dados</div>';
    return;
  }
  const data = [{
    type: 'indicator', mode: 'gauge+number', value: valor,
    number: { font: { color: '#fff', size: 36 }, suffix: '' },
    gauge: {
      axis: { range: [0, 100], tickcolor: COR.textoSec, tickfont: { size: 9, color: COR.textoSec } },
      bar: { color: cor, thickness: .82 },
      bgcolor: 'rgba(0,0,0,0)',
      borderwidth: 0,
      steps: [
        { range: [0, 35], color: 'rgba(239,74,99,0.14)' },
        { range: [35, 55], color: 'rgba(242,181,68,0.12)' },
        { range: [55, 75], color: 'rgba(124,108,240,0.12)' },
        { range: [75, 100], color: 'rgba(34,197,94,0.14)' },
      ],
    },
  }];
  plotlySeguro(elId, data, { ...PLOTLY_DARK, height: 170 }, PLOTLY_CONFIG);
}

function renderScores() {
  const inv = dados.scores.momento_investimento;
  const ma = dados.scores.ma_score;
  renderGauge('gauge-investimento', inv.score, 'Momento de Investimento', COR.accent);
  document.getElementById('nivel-investimento').textContent = inv.nivel || '—';
  renderGauge('gauge-ma', ma.score, 'M&A Score', COR.verde);
  document.getElementById('nivel-ma').textContent = `${ma.emoji || ''} ${ma.nivel || '—'}`;
}

// ===== Insights =====
function renderInsights() {
  document.getElementById('lista-insights').innerHTML = (dados.insights || []).map(i =>
    `<li class="${esc(i.tipo)}">${esc(i.texto)}</li>`
  ).join('') || '<li>Sem leituras no momento.</li>';
}

// ===== Alertas =====
function renderAlertas() {
  const box = document.getElementById('alertas-banner');
  const ativos = dados.alertas || [];
  if (!ativos.length) { box.style.display = 'none'; return; }
  box.style.display = 'flex';
  box.innerHTML = ativos.map(a => `<span>${esc(a.mensagem)}</span>`).join('');
}

// ===== Tabelas telecom =====
function renderTelecomTabelas() {
  const grupos = dados.telecom_grupos || {};
  const linhasGrupos = Object.values(grupos).map(g => {
    const perfil = (g.historico && g.historico[0]) || {};
    const mercado = g.valor !== null && g.valor !== undefined
      ? `${fmtNum(g.valor, 2)} ${g.variacao_dia != null ? (g.variacao_dia >= 0 ? '▲' : '▼') + fmtNum(Math.abs(g.variacao_dia)) + '%' : ''}`
      : '—';
    return `<tr><td class="op">${esc(perfil.nome || '—')}</td><td>${esc(perfil.tipo || '—')}</td><td>${esc(perfil.segmento || '—')}</td><td>${mercado}</td></tr>`;
  }).join('');
  document.querySelector('#tabela-grupos tbody').innerHTML = linhasGrupos || '<tr><td colspan="4">Sem dados.</td></tr>';

  const movs = (dados.telecom_setor.telecom_movimentacoes && dados.telecom_setor.telecom_movimentacoes.historico) || [];
  document.querySelector('#tabela-movs tbody').innerHTML = movs.map(mv => `
    <tr>
      <td>${esc(mv.periodo)}</td>
      <td class="op">${esc(mv.operacao)}</td>
      <td>${esc(mv.regiao || '—')}</td>
      <td>${esc(mv.obs || '—')}<br><span class="fonte-cel">Fonte: ${esc(mv.fonte || '—')}</span></td>
    </tr>`).join('') || '<tr><td colspan="4">Sem registros.</td></tr>';

  const riscos = (dados.telecom_setor.telecom_riscos_regulatorios && dados.telecom_setor.telecom_riscos_regulatorios.historico) || [];
  document.getElementById('lista-riscos').innerHTML = riscos.map(r => `<li>${esc(r.risco)}</li>`).join('');
}

// ===== Gráficos Plotly =====
function serieHistorico(item) {
  const h = (item && item.historico) || [];
  return { x: h.map(p => p.data), y: h.map(p => p.valor) };
}

// Título padrão de gráfico Plotly, consistente com o resto do painel
// (maiúsculas, letter-spacing, cor secundária) em vez do estilo padrão do Plotly.
function tituloChart(txt) {
  return { text: txt.toUpperCase(), font: { size: 10.5, color: COR.textoSec }, x: 0, xanchor: 'left' };
}
const EIXO = { color: COR.textoSec, gridcolor: 'rgba(255,255,255,0.05)', zerolinecolor: 'rgba(255,255,255,0.08)' };

// Bandas de referência pra normalizar o radar macro. Selic (%), IPCA 12m
// (%) e Desemprego (%) são grandezas pequenas (0-20); Produção Industrial e
// Vendas no Varejo são ÍNDICES (base 100, variam 85-115) — plotar tudo no
// mesmo eixo 0-100 fazia os três primeiros sumirem no centro do radar e os
// dois últimos estourarem o raio. Cada eixo agora vira um "score" 0-100
// relativo à sua própria banda plausível, só pra desenho — o valor real
// (com unidade) aparece no hover.
const BANDAS_RADAR = {
  'Selic':         { min: 0,  max: 20,  valor: e => e.selic_meta,          unidade: '% a.a.' },
  'IPCA 12m':      { min: -2, max: 12,  valor: e => e.ipca_12m,            unidade: '%' },
  'Desemprego':    { min: 3,  max: 15,  valor: e => e.desemprego,          unidade: '%' },
  'Produção Ind.': { min: 85, max: 115, valor: e => e.producao_industrial, unidade: 'índice' },
  'Varejo':        { min: 85, max: 115, valor: e => e.vendas_varejo,       unidade: 'índice' },
};

function renderChartsEconomia() {
  const e = dados.economia;
  const labels = Object.keys(BANDAS_RADAR);
  const brutos = labels.map(l => { const b = BANDAS_RADAR[l].valor(e); return b && b.valor; });
  if (brutos.every(v => v === null || v === undefined)) {
    graficoVazio('chart-radar-economia', 'nenhum indicador macro foi buscado ainda com internet');
  } else {
    const scores = labels.map((l, i) => {
      const { min, max } = BANDAS_RADAR[l];
      const v = brutos[i];
      if (v === null || v === undefined) return 0;
      return Math.max(0, Math.min(100, ((v - min) / (max - min)) * 100));
    });
    const textoHover = labels.map((l, i) => {
      const v = brutos[i];
      const txt = v === null || v === undefined ? 'sem dado' : `${fmtNum(v, 1)} ${BANDAS_RADAR[l].unidade}`;
      return `${l}: ${txt}`;
    });
    plotlySeguro('chart-radar-economia', [{
      type: 'scatterpolar', r: scores, theta: labels, fill: 'toself',
      line: { color: COR.accent }, fillcolor: COR.accentSoft,
      text: textoHover, hovertemplate: '%{text}<extra></extra>',
    }], {
      ...PLOTLY_DARK,
      polar: {
        bgcolor: 'rgba(0,0,0,0)',
        radialaxis: { color: COR.textoSec, gridcolor: 'rgba(255,255,255,0.06)', range: [0, 100], showticklabels: false },
        angularaxis: { color: COR.texto },
      },
      showlegend: false,
      title: tituloChart('Radar macro (posição relativa — passe o mouse pro valor real)'),
    }, PLOTLY_CONFIG);
  }

  const s = serieHistorico(e.ipca_mensal);
  if (s.x.length === 0) {
    graficoVazio('chart-linha-inflacao', 'série do IPCA ainda não foi buscada');
  } else {
    plotlySeguro('chart-linha-inflacao', [{ x: s.x, y: s.y, type: 'scatter', mode: 'lines', line: { color: COR.amarelo, width: 2 } }],
      { ...PLOTLY_DARK, title: tituloChart('IPCA mensal (%)'), xaxis: { ...EIXO, type: 'date' }, yaxis: EIXO }, PLOTLY_CONFIG);
  }
}

function renderChartsMercado() {
  const m = dados.mercado;
  const sd = serieHistorico(m.dolar_ptax);
  if (sd.x.length === 0) {
    graficoVazio('chart-linha-dolar', 'cotação do dólar ainda não foi buscada');
  } else {
    plotlySeguro('chart-linha-dolar', [{ x: sd.x, y: sd.y, type: 'scatter', mode: 'lines', fill: 'tozeroy', line: { color: COR.accent, width: 2 }, fillcolor: COR.accentSoft }],
      { ...PLOTLY_DARK, title: tituloChart('Dólar (USD/BRL)'), xaxis: { ...EIXO, type: 'date' }, yaxis: EIXO }, PLOTLY_CONFIG);
  }

  const si = serieHistorico(m.ibovespa);
  if (si.x.length === 0) {
    graficoVazio('chart-linha-ibov', 'série do Ibovespa ainda não foi buscada');
  } else {
    plotlySeguro('chart-linha-ibov', [{ x: si.x, y: si.y, type: 'scatter', mode: 'lines', line: { color: COR.verde, width: 2 } }],
      { ...PLOTLY_DARK, title: tituloChart('Ibovespa'), xaxis: { ...EIXO, type: 'date' }, yaxis: EIXO }, PLOTLY_CONFIG);
  }

  // Rótulos legíveis (a chave crua "dow_jones" virava um "dow jon-" cortado
  // e girado 45° no eixo — trocado por um bar horizontal com nome completo
  // e valor escrito, bem mais fácil de ler que a cor de uma célula de heatmap).
  const NOMES_MERCADO = {
    dolar_ptax: 'USD/BRL', euro_ptax: 'EUR/BRL', ibovespa: 'Ibovespa', sp500: 'S&P 500',
    nasdaq: 'Nasdaq', dow_jones: 'Dow Jones', ouro: 'Ouro', petroleo: 'Petróleo (WTI)', vix: 'VIX',
  };
  const chaves = Object.keys(NOMES_MERCADO);
  const variacoesBrutas = chaves.map(k => m[k] && m[k].variacao_dia);
  if (variacoesBrutas.every(v => v === null || v === undefined)) {
    graficoVazio('chart-heatmap-mercado', 'nenhuma variação diária disponível ainda');
  } else {
    // Maior variação (em módulo) primeiro embaixo por causa da orientação
    // horizontal do Plotly (desenha de baixo pra cima) — assim a barra mais
    // extrema fica no topo visualmente.
    const pares = chaves.map((k, i) => ({ k, v: variacoesBrutas[i] ?? 0 })).sort((a, b) => Math.abs(a.v) - Math.abs(b.v));
    const nomes = pares.map(p => NOMES_MERCADO[p.k]);
    const valores = pares.map(p => p.v);
    const maxAbs = Math.max(...valores.map(v => Math.abs(v)), 0.5);
    plotlySeguro('chart-heatmap-mercado', [{
      x: valores, y: nomes, type: 'bar', orientation: 'h',
      marker: { color: valores.map(v => v >= 0 ? COR.verde : COR.vermelho) },
      text: valores.map(v => (v >= 0 ? '▲ ' : '▼ ') + fmtNum(Math.abs(v), 2) + '%'),
      textposition: 'outside', textfont: { color: COR.textoSec, size: 10.5 },
      cliponaxis: false,
    }], {
      ...PLOTLY_DARK,
      title: tituloChart('Variação do dia (%)'),
      xaxis: { ...EIXO, range: [-maxAbs * 1.4, maxAbs * 1.4], zeroline: true, zerolinewidth: 1.5 },
      yaxis: { ...EIXO, type: 'category', automargin: true },
      margin: { t: 34, l: 90, r: 40, b: 34 },
    }, PLOTLY_CONFIG);
  }
}

function renderChartsTelecom() {
  // O treemap antigo usava o "valor" de cada grupo como tamanho — mas esse
  // valor é a COTAÇÃO POR AÇÃO (R$/US$ por papel), não o tamanho da empresa,
  // e pras de capital fechado nem existe (era preenchido com 10 só pra
  // aparecer uma caixinha). Resultado: American Tower (ação ~US$163)
  // engolia o quadro todo, sem dizer nada de real sobre porte relativo.
  // Troca por um gráfico do que realmente é comparável entre os grupos de
  // capital aberto: a variação do dia (%) da ação. Os de capital fechado
  // continuam listados (com tipo/segmento) na tabela "Grandes grupos" logo
  // abaixo — não têm dado de mercado público pra plotar, e está tudo bem
  // não inventar um número só pra preencher espaço.
  const grupos = Object.values(dados.telecom_grupos || {});
  const abertos = grupos
    .map(g => ({ nome: (g.historico && g.historico[0] && g.historico[0].nome) || '?', variacao: g.variacao_dia }))
    .filter(g => g.variacao !== null && g.variacao !== undefined);
  if (abertos.length === 0) {
    graficoVazio('chart-treemap-grupos', 'nenhuma cotação dos grupos de capital aberto foi buscada ainda');
  } else {
    const ordenado = [...abertos].sort((a, b) => a.variacao - b.variacao);
    const nomes = ordenado.map(g => g.nome);
    const valores = ordenado.map(g => g.variacao);
    const maxAbs = Math.max(...valores.map(v => Math.abs(v)), 0.5);
    plotlySeguro('chart-treemap-grupos', [{
      x: valores, y: nomes, type: 'bar', orientation: 'h',
      marker: { color: valores.map(v => v >= 0 ? COR.verde : COR.vermelho) },
      text: valores.map(v => (v >= 0 ? '▲ ' : '▼ ') + fmtNum(Math.abs(v), 2) + '%'),
      textposition: 'outside', textfont: { color: COR.textoSec, size: 10.5 },
      cliponaxis: false,
    }], {
      ...PLOTLY_DARK,
      title: tituloChart('Ações do setor — variação do dia (%)'),
      xaxis: { ...EIXO, range: [-maxAbs * 1.4, maxAbs * 1.4], zeroline: true, zerolinewidth: 1.5 },
      yaxis: { ...EIXO, type: 'category', automargin: true },
      margin: { t: 34, l: 110, r: 40, b: 34 },
    }, PLOTLY_CONFIG);
  }

  const t = dados.telecom_setor;
  if (t.multiplo_ev_ebitda_atual) {
    plotlySeguro('chart-barra-multiplo', [{
      x: ['2021', 'Hoje'], y: [t.multiplo_ev_ebitda_2021.valor, t.multiplo_ev_ebitda_atual.valor],
      type: 'bar', marker: { color: ['rgba(124,108,240,0.35)', COR.accent] }, width: [.5, .5]
    }], { ...PLOTLY_DARK, title: tituloChart('Múltiplo EV/EBITDA (x)'), xaxis: { ...EIXO, type: 'category' }, yaxis: EIXO }, PLOTLY_CONFIG);
  }
}

// ===== Ranking de provedores (base de clientes) =====
// Função genérica: serve tanto pro ranking nacional (campo acessos_mil, em
// milhares) quanto pros estaduais (campo acessos, valor cheio) — só muda a
// chave do campo numérico, o texto da unidade e o título.
function renderChartRanking(elId, chave, campoValor, unidadeTxt, titulo) {
  const item = (dados.telecom_ranking || {})[chave];
  const lista = (item && item.historico) || [];
  if (lista.length === 0) {
    graficoVazio(elId, 'ranking ainda não foi carregado');
    return;
  }
  // Já vem ordenado por base de clientes (maior primeiro); Plotly desenha
  // barras horizontais de baixo pra cima, então invertemos pra o 1º lugar
  // aparecer no topo.
  const ordenado = [...lista].sort((a, b) => b[campoValor] - a[campoValor]).reverse();
  const nomes = ordenado.map(p => p.nome);
  const valores = ordenado.map(p => p[campoValor]);
  const maxValor = Math.max(...valores);
  const cores = ordenado.map((_, i) => i === ordenado.length - 1 ? COR.accent : `rgba(124,108,240,${0.35 + (i / ordenado.length) * 0.4})`);
  plotlySeguro(elId, [{
    x: valores, y: nomes, type: 'bar', orientation: 'h',
    marker: { color: cores },
    text: valores.map(v => fmtNum(v, 0) + (unidadeTxt ? ' ' + unidadeTxt : '')), textposition: 'outside',
    textfont: { color: COR.textoSec, size: 10.5 },
    // cliponaxis:false evita que o texto do rótulo (fora da barra) seja
    // cortado pelo clip-path da área de plotagem quando o valor chega perto
    // do fim do eixo — sem isso, o número do 1º colocado (a maior barra)
    // aparecia cortado tipo "1.2" em vez de "122.502".
    cliponaxis: false,
  }], {
    ...PLOTLY_DARK,
    title: tituloChart(titulo),
    // Range explícito com folga de 22% à direita: dá espaço pro rótulo da
    // barra mais longa (que encosta no fim do eixo) sem depender só do
    // cliponaxis, e evita que o Plotly recalcule um range justo demais.
    xaxis: { ...EIXO, range: [0, maxValor * 1.22], title: { text: unidadeTxt || 'acessos', font: { size: 10, color: COR.textoSec } } },
    // type:'category' precisa vir explícito — o Plotly (nesta versão) não
    // detectou sozinho que o eixo y de uma barra horizontal com nomes de
    // operadora era categórico, e desenhava um eixo numérico vazio (mesmo
    // bug de fundo que já tínhamos corrigido nos outros gráficos).
    yaxis: { ...EIXO, type: 'category', automargin: true },
    margin: { t: 34, l: 140, r: 60, b: 34 },
  }, PLOTLY_CONFIG);
}

function renderChartRankingNacional() {
  renderChartRanking('chart-ranking-nacional', 'ranking_nacional', 'acessos', '', 'Top 10 provedores do Brasil — base de clientes (acessos)');
  renderChartRanking('chart-ranking-ro', 'ranking_ro', 'acessos', '', 'Top 10 — Rondônia (RO)');
  renderChartRanking('chart-ranking-mt', 'ranking_mt', 'acessos', '', 'Top 10 — Mato Grosso (MT)');
  renderChartRanking('chart-ranking-to', 'ranking_to', 'acessos', '', 'Top 10 — Tocantins (TO)');
  renderChartRanking('chart-ranking-pa', 'ranking_pa', 'acessos', '', 'Top 10 — Pará (PA)');
  renderChartRanking('chart-ranking-ms', 'ranking_ms', 'acessos', '', 'Top 10 — Mato Grosso do Sul (MS)');
}

function renderChartHistoricoScores() {
  const h = dados.historico_scores || [];
  if (h.length < 2) {
    // Com 0 ou 1 ponto o Plotly não tem como calcular um range de data
    // sensato e desenha um eixo degenerado (ex.: milissegundos) — melhor
    // mostrar uma mensagem clara do que esse eixo quebrado.
    graficoVazio('chart-historico-scores', 'o histórico começa a aparecer a partir do 2º dia de atualização automática');
    return;
  }
  plotlySeguro('chart-historico-scores', [
    { x: h.map(p => p.data), y: h.map(p => p.momento_investimento), type: 'scatter', mode: 'lines+markers', name: 'Momento de Investimento', line: { color: COR.accent, width: 2 }, marker: { size: 5 } },
    { x: h.map(p => p.data), y: h.map(p => p.ma_score), type: 'scatter', mode: 'lines+markers', name: 'M&A Score', line: { color: COR.verde, width: 2 }, marker: { size: 5 } },
  ], { ...PLOTLY_DARK, legend: { font: { color: COR.textoSec, size: 10.5 }, orientation: 'h', y: 1.15 }, xaxis: { ...EIXO, type: 'category' }, yaxis: { ...EIXO, range: [0, 100] } }, PLOTLY_CONFIG);
}

function render() {
  if (!dados) return;
  // Cada seção roda isolada: se uma travar (ex.: gráfico com dado
  // inesperado), as outras continuam renderizando normalmente.
  const passos = [
    renderTicker, renderKpis, renderScores, renderInsights, renderAlertas,
    renderTelecomTabelas, renderChartsEconomia, renderChartsMercado,
    renderChartsTelecom, renderChartRankingNacional, renderChartHistoricoScores,
  ];
  for (const passo of passos) {
    try { passo(); } catch (e) { console.warn(`falha ao renderizar ${passo.name}`, e); }
  }
}

const btnAtualizar = document.getElementById('btn-atualizar');
if (btnAtualizar) btnAtualizar.addEventListener('click', atualizarAgora);

relogio();
setInterval(relogio, 1000);

if (typeof DADOS_ESTATICOS !== 'undefined') {
  // Snapshot estático (publicado no GitHub Pages) — dados já vêm embutidos na página.
  dados = DADOS_ESTATICOS;
  render();
} else {
  // Painel rodando local via start.command — busca dados ao vivo da API Flask.
  carregar();
  setInterval(carregar, 30000);
}
