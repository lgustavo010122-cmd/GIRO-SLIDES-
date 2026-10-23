"""Editor do banco giro.db pela linha de comando.

Exemplos:
  python admin.py produtos                                   # lista o catálogo
  python admin.py adicionar "Onda Max" "Verde" img/onda-max-verde.jpg --preco "R$ 19,90"
  python admin.py editar 3 --preco "R$ 17,50" --cor "Azul"
  python admin.py esconder 5      /  python admin.py mostrar 5
  python admin.py remover 5
  python admin.py config                                     # lista textos e WhatsApp
  python admin.py config whatsapp 5531988887777              # altera um texto
Depois de alterar, rode `python build.py` para ver o site, ou só faça commit/push:
o GitHub gera e publica o site sozinho.
"""
import argparse, sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
con = sqlite3.connect(RAIZ / "giro.db")
con.row_factory = sqlite3.Row


def listar(_):
    print(f"{'id':>3}  {'ordem':>5}  {'ativo':5}  {'modelo':<14} {'cor':<14} {'preço':<12} imagem")
    for p in con.execute("SELECT * FROM produtos ORDER BY ordem, id"):
        print(f"{p['id']:>3}  {p['ordem']:>5}  {'sim' if p['ativo'] else 'não':5}  "
              f"{p['modelo']:<14} {p['cor']:<14} {p['preco']:<12} {p['imagem']}")


def checar_imagem(caminho):
    if not (RAIZ / "static" / caminho).exists():
        print(f"Atenção: static/{caminho} ainda não existe. Coloque a foto lá antes de publicar.")


def adicionar(a):
    ordem = a.ordem or (con.execute("SELECT COALESCE(MAX(ordem),0)+1 FROM produtos").fetchone()[0])
    cur = con.execute("INSERT INTO produtos(modelo,cor,imagem,preco,ordem) VALUES (?,?,?,?,?)",
                      (a.modelo, a.cor, a.imagem, a.preco, ordem))
    con.commit(); checar_imagem(a.imagem)
    print(f"Produto {cur.lastrowid} adicionado.")


def editar(a):
    campos = {k: v for k, v in vars(a).items() if k in ("modelo", "cor", "imagem", "preco", "ordem") and v is not None}
    if not campos:
        raise SystemExit("Nada para alterar. Use --modelo, --cor, --imagem, --preco ou --ordem.")
    sets = ", ".join(f"{k}=?" for k in campos)
    n = con.execute(f"UPDATE produtos SET {sets} WHERE id=?", (*campos.values(), a.id)).rowcount
    con.commit()
    if "imagem" in campos: checar_imagem(campos["imagem"])
    print("Atualizado." if n else f"Produto {a.id} não existe.")


def ativo(valor):
    def f(a):
        n = con.execute("UPDATE produtos SET ativo=? WHERE id=?", (valor, a.id)).rowcount
        con.commit(); print("Feito." if n else f"Produto {a.id} não existe.")
    return f


def remover(a):
    n = con.execute("DELETE FROM produtos WHERE id=?", (a.id,)).rowcount
    con.commit(); print("Removido." if n else f"Produto {a.id} não existe.")


def config(a):
    if a.chave is None:
        for r in con.execute("SELECT chave, valor FROM config ORDER BY chave"):
            print(f"{r['chave']:<20} {r['valor']}")
        return
    if a.valor is None:
        r = con.execute("SELECT valor FROM config WHERE chave=?", (a.chave,)).fetchone()
        print(r["valor"] if r else f"Chave '{a.chave}' não existe."); return
    con.execute("INSERT INTO config(chave,valor) VALUES (?,?) ON CONFLICT(chave) DO UPDATE SET valor=excluded.valor",
                (a.chave, a.valor))
    con.commit(); print(f"{a.chave} = {a.valor}")


ap = argparse.ArgumentParser(description="Editor do catálogo Giro Slides")
sub = ap.add_subparsers(required=True)
sub.add_parser("produtos", help="lista os produtos").set_defaults(f=listar)

s = sub.add_parser("adicionar", help="adiciona um produto")
s.add_argument("modelo"); s.add_argument("cor"); s.add_argument("imagem", help="ex.: img/minha-foto.jpg")
s.add_argument("--preco", default="Consulte"); s.add_argument("--ordem", type=int)
s.set_defaults(f=adicionar)

s = sub.add_parser("editar", help="altera um produto pelo id")
s.add_argument("id", type=int)
for c in ("modelo", "cor", "imagem", "preco"): s.add_argument(f"--{c}")
s.add_argument("--ordem", type=int); s.set_defaults(f=editar)

for nome, val in (("esconder", 0), ("mostrar", 1)):
    s = sub.add_parser(nome, help=f"{nome} um produto no site"); s.add_argument("id", type=int); s.set_defaults(f=ativo(val))
s = sub.add_parser("remover", help="apaga um produto"); s.add_argument("id", type=int); s.set_defaults(f=remover)

s = sub.add_parser("config", help="lista ou altera textos/WhatsApp")
s.add_argument("chave", nargs="?"); s.add_argument("valor", nargs="?"); s.set_defaults(f=config)

args = ap.parse_args(); args.f(args)
