# Giro Slides — site de atacado

[Ver o site publicado](https://lgustavo010122-cmd.github.io/GIRO-SLIDES-/#catalogo)

O conteúdo do site (produtos, preços, cores, WhatsApp e textos) fica no banco **SQLite `giro.db`**.
O arquivo `build.py` lê o banco e gera o site na pasta `dist/`. No GitHub, isso acontece sozinho a cada push.

```
giro.db            banco de dados (produtos + textos)
schema.sql         estrutura das tabelas
template.html      layout do site, com marcadores {{chave}}
static/img/        fotos dos chinelos
build.py           gera o site em dist/
admin.py           edita o banco pela linha de comando
.github/workflows/ publicação automática no GitHub Pages
```

## Como alterar o site

Precisa só de Python 3 (não instala nada).

```bash
python admin.py produtos                       # ver o catálogo com os ids
python admin.py editar 3 --preco "R$ 17,50"    # mudar preço
python admin.py esconder 5                     # tirar do site sem apagar
python admin.py config whatsapp 5531988887777  # seu número (país + DDD + número)
python admin.py config                         # ver todos os textos editáveis
```

Produto novo: coloque a foto em `static/img/` e rode

```bash
python admin.py adicionar "Onda Max" "Verde" img/onda-max-verde.jpg --preco "Consulte"
```

Uma cor nova aparece sozinha como filtro no catálogo.

Para conferir antes de publicar: `python build.py` e abra `dist/index.html`.

Para publicar:

```bash
git add giro.db static
git commit -m "Atualiza catálogo"
git push
```

Também dá para abrir o `giro.db` num programa visual, como o **DB Browser for SQLite** (gratuito), editar as tabelas `produtos` e `config` e depois fazer o push.

## Ligar o GitHub Pages (uma vez só)

No repositório: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
Depois disso, cada push na branch `main` publica o site em alguns segundos (aba **Actions** mostra o andamento).

## Tabelas

**config** (`chave`, `valor`): `whatsapp`, `marca`, `titulo_pagina`, `hero_titulo`, `hero_subtitulo`, `pedido_minimo`, `catalogo_subtitulo`, `cta_titulo`, `cta_subtitulo`, `rodape`, `rodape_aviso`, `imagem_destaque`.

**produtos**: `id`, `modelo`, `cor`, `imagem`, `preco`, `ordem` (posição no catálogo), `ativo` (1 aparece, 0 escondido).
