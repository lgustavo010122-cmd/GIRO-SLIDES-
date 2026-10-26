"""Gera o site a partir do banco giro.db.
Saída: pasta dist/ (index.html + img/), pronta para o GitHub Pages.
Uso: python build.py
"""
import html, json, re, shutil, sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DIST = RAIZ / "dist"


def js(valor):
    # JSON seguro para colocar dentro de <script>
    return json.dumps(valor, ensure_ascii=False).replace("</", "<\\/")


def main():
    con = sqlite3.connect(RAIZ / "giro.db")
    con.row_factory = sqlite3.Row
    cfg = {r["chave"]: r["valor"] for r in con.execute("SELECT chave, valor FROM config")}
    prods = con.execute(
        "SELECT modelo, cor, imagem, preco FROM produtos WHERE ativo=1 ORDER BY ordem, id"
    ).fetchall()

    for p in prods:
        if not (RAIZ / "static" / p["imagem"]).exists():
            raise SystemExit(f"Imagem não encontrada: static/{p['imagem']} ({p['modelo']} {p['cor']})")

    cores = list(dict.fromkeys(p["cor"] for p in prods))
    numero = re.sub(r"\D", "", cfg.get("whatsapp", ""))
    imagem_destaque = cfg.get("imagem_destaque", prods[0]["imagem"] if prods else "")
    foto_inicial = next((p for p in prods if p["imagem"] == imagem_destaque), None)
    fotos_destaque = []
    imagens_vistas = set()
    if imagem_destaque:
        fotos_destaque.append({
            "img": imagem_destaque,
            "n": foto_inicial["modelo"] if foto_inicial else "Destaque atual",
            "c": foto_inicial["cor"] if foto_inicial else "",
        })
        imagens_vistas.add(imagem_destaque)
    for p in prods:
        if p["imagem"] not in imagens_vistas:
            fotos_destaque.append({"img": p["imagem"], "n": p["modelo"], "c": p["cor"]})
            imagens_vistas.add(p["imagem"])

    valores = {k: html.escape(v) for k, v in cfg.items()}
    lista = [c.lower() if i else c for i, c in enumerate(cores)]
    valores["cores_texto"] = html.escape(", ".join(lista[:-1]) + " e " + lista[-1] if len(lista) > 1 else "".join(lista))
    valores["whatsapp_js"] = js(numero)
    valores["produtos_js"] = js([{"n": p["modelo"], "c": p["cor"], "img": p["imagem"], "p": p["preco"]} for p in prods])
    valores["fotos_destaque_js"] = js(fotos_destaque)
    valores["cores_js"] = js(["Todos"] + cores)
    valores["imagem_destaque_js"] = js(imagem_destaque)

    tpl = (RAIZ / "template.html").read_text(encoding="utf-8")
    saida = re.sub(r"\{\{(\w+)\}\}", lambda m: valores.get(m.group(1), m.group(0)), tpl)
    faltando = set(re.findall(r"\{\{(\w+)\}\}", saida))
    if faltando:
        raise SystemExit(f"Chaves sem valor no banco: {', '.join(sorted(faltando))}")

    shutil.rmtree(DIST, ignore_errors=True)
    shutil.copytree(RAIZ / "static", DIST)
    (DIST / "index.html").write_text(saida, encoding="utf-8")
    print(f"Site gerado em dist/ — {len(prods)} produtos, {len(cores)} cores.")


if __name__ == "__main__":
    main()
