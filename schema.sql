-- Banco do site Giro Slides (SQLite)
-- Textos e configurações gerais do site (chave -> valor)
CREATE TABLE IF NOT EXISTS config (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);

-- Catálogo de chinelos
CREATE TABLE IF NOT EXISTS produtos (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    modelo  TEXT NOT NULL,                 -- ex.: Onda Sport
    cor     TEXT NOT NULL,                 -- ex.: Preto (vira um filtro no catálogo)
    imagem  TEXT NOT NULL,                 -- caminho dentro de static/, ex.: img/foto-01.jpg
    preco   TEXT NOT NULL DEFAULT 'Consulte',
    ordem   INTEGER NOT NULL DEFAULT 0,    -- posição no catálogo
    ativo   INTEGER NOT NULL DEFAULT 1     -- 0 = escondido do site
);
