"""Migração única: lê o HTML original (com fotos em base64) e gera
   - static/img/*.jpg       (as fotos, agora como arquivos)
   - template.html          (o site com marcadores {{chave}})
   - giro.db                (banco SQLite com produtos e textos)
Uso: python tools/migrar_html_original.py caminho/do/original.html
"""
import base64, re, sqlite3, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
src = Path(sys.argv[1]).read_text(encoding="utf-8")

# 1) fotos -> arquivos
m = re.search(r'var IMG=\[(.*?)\];', src, re.S)
uris = re.findall(r'"data:image/(\w+);base64,([^"]+)"', m.group(1))
nomes = ["foto-01", "foto-02", "foto-03", "foto-04", "foto-05", "foto-06", "foto-07", "foto-08", "foto-09"]
(RAIZ / "static/img").mkdir(parents=True, exist_ok=True)
arquivos = []
for nome, (ext, b64) in zip(nomes, uris):
    ext = "jpg" if ext == "jpeg" else ext
    f = f"img/{nome}.{ext}"
    (RAIZ / "static" / f).write_bytes(base64.b64decode(b64))
    arquivos.append(f)

# 2) produtos do array P
prods = re.findall(r'\{n:"([^"]+)",c:"([^"]+)",i:(\d+),p:"([^"]+)"\}', src)

# 3) template com marcadores
textos = {
    "titulo_pagina": "Giro Slides | Chinelos no Atacado para Lojistas",
    "marca": "GIRO SLIDES",
    "hero_titulo": "Conforto que gira o seu estoque.",
    "hero_subtitulo": "Design moderno. Conforto máximo. Chinelos slide em condições de atacado para lojistas.",
    "pedido_minimo": "12 pares",
    "catalogo_subtitulo": "Escolha o modelo para falar com um atendente, ou monte uma cotação com vários itens.",
    "cta_titulo": "Pronto para renovar o estoque da sua loja?",
    "cta_subtitulo": "Fale com nosso time comercial e receba uma cotação.",
    "rodape": "© 2026 Giro Slides · Conforto que gira o seu estoque",
    "rodape_aviso": "Vendas exclusivas para lojistas (CNPJ)",
}
t = src
def troca(antigo, novo, n=None):
    global t
    c = t.count(antigo)
    assert c and (n is None or c == n), (antigo[:60], c)
    t = t.replace(antigo, novo)

troca(f"<title>{textos['titulo_pagina']}</title>", "<title>{{titulo_pagina}}</title>")
troca('href="#">GIRO SLIDES</a>', 'href="#">{{marca}}</a>')
troca(f"<h1>{textos['hero_titulo']}</h1>", "<h1>{{hero_titulo}}</h1>")
troca(f"<p>{textos['hero_subtitulo']}</p>", "<p>{{hero_subtitulo}}</p>")
troca("<b>12 pares</b>", "<b>{{pedido_minimo}}</b>")
troca("compras a partir de 12 pares.", "compras a partir de {{pedido_minimo}}.")
troca(f"<p>{textos['catalogo_subtitulo']}</p>", "<p>{{catalogo_subtitulo}}</p>")
troca(f"<h2>{textos['cta_titulo']}</h2>", "<h2>{{cta_titulo}}</h2>")
troca(f"<p>{textos['cta_subtitulo']}</p>", "<p>{{cta_subtitulo}}</p>")
troca(f"<span>{textos['rodape']}</span>", "<span>{{rodape}}</span>")
troca(f"<span>{textos['rodape_aviso']}</span>", "<span>{{rodape_aviso}}</span>")
troca("Preto, branco, azul-marinho e off-white para montar o seu mix.", "{{cores_texto}} para montar o seu mix.")

# script: dados vêm do banco
ini = t.index("// ✏️ TROQUE PELO SEU NÚMERO")
fim = t.index("var cats=")
t = t[:ini] + "var WHATSAPP={{whatsapp_js}};\nvar P={{produtos_js}};\n" + t[fim:]
troca('var cats=["Todos","Preto","Branco","Azul-marinho","Off-white"]', "var cats={{cores_js}}")
troca('$("himg").src=IMG[7];', '$("himg").src={{imagem_destaque_js}};')
troca("IMG[x.i]", "x.img")
troca("IMG[P[ids[0]].i]", "P[ids[0]].img")
(RAIZ / "template.html").write_text(t, encoding="utf-8")

# 4) banco
db = RAIZ / "giro.db"
db.unlink(missing_ok=True)
con = sqlite3.connect(db)
con.executescript((RAIZ / "schema.sql").read_text(encoding="utf-8"))
textos.update({"whatsapp": "5531999999999", "imagem_destaque": arquivos[7]})
con.executemany("INSERT INTO config(chave, valor) VALUES (?,?)", textos.items())
con.executemany(
    "INSERT INTO produtos(modelo, cor, imagem, preco, ordem) VALUES (?,?,?,?,?)",
    [(n, c, arquivos[int(i)], p, k + 1) for k, (n, c, i, p) in enumerate(prods)],
)
con.commit()
print(f"{len(arquivos)} fotos, {len(prods)} produtos, {len(textos)} textos -> giro.db")
