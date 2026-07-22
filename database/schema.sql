-- Economic Intelligence Dashboard (Grupo Netway) — esquema SQLite
-- Guarda o último valor bom conhecido de cada indicador (cache/resiliência
-- contra APIs fora do ar) e o histórico dos scores calculados por nós
-- (Momento de Investimento e M&A Score), que não existem em nenhuma API.

CREATE TABLE IF NOT EXISTS cache_indicadores (
  chave           TEXT PRIMARY KEY,
  categoria       TEXT,
  valor           REAL,
  unidade         TEXT,
  data_referencia TEXT,
  variacao_dia    REAL,
  fonte           TEXT,
  atualizacao     TEXT,        -- 'automatica' | 'manual'
  historico_json  TEXT,        -- lista [{"data":"...", "valor":...}, ...]
  atualizado_em   TEXT
);

CREATE TABLE IF NOT EXISTS historico_scores (
  id                   INTEGER PRIMARY KEY AUTOINCREMENT,
  data                 TEXT NOT NULL,
  momento_investimento INTEGER,
  ma_score             INTEGER,
  criado_em            TEXT
);

CREATE TABLE IF NOT EXISTS alertas_log (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  chave      TEXT,
  mensagem   TEXT,
  nivel      TEXT,     -- 'info' | 'atencao' | 'critico'
  ativo      INTEGER DEFAULT 1,
  criado_em  TEXT,
  resolvido_em TEXT
);
